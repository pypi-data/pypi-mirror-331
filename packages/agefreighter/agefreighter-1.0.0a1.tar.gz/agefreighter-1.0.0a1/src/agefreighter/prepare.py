#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import concurrent.futures
import logging
import os
import sys
import time
from typing import Any, Dict, Generator

import pandas as pd

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CsvDataManager:
    """
    Manage CSV file operations, including loading a DataFrame and chunking.
    """

    def __init__(
        self, data_dir: str = None, base_file: str = "customer_product_bought"
    ) -> None:
        if data_dir is None:
            data_dir = os.path.abspath(os.path.join("..", "data", "transaction"))
        self.data_dir = data_dir
        self.base_file = base_file
        self.csv_file = os.path.join(self.data_dir, f"{self.base_file}.csv")

    def get_dataframe(self) -> pd.DataFrame:
        """
        Read the CSV file and return a DataFrame.
        """
        return pd.read_csv(self.csv_file)

    @staticmethod
    def get_chunks(
        df: pd.DataFrame, chunk_size: int
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Yield chunks of the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to be chunked.
            chunk_size (int): Number of rows per chunk.

        Yields:
            Generator[pd.DataFrame, None, None]: Chunks of the DataFrame.
        """
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i : i + chunk_size].copy()


class Neo4jLoader:
    """
    Load CSV data into Neo4j.
    """

    from neo4j import AsyncGraphDatabase

    def __init__(self, csv_manager: CsvDataManager) -> None:
        self.csv_manager = csv_manager

    async def load_data(self) -> None:
        log.info("Loading CSV to Neo4j")
        try:
            n4j_uri = os.environ["NEO4J_URI"]
            n4j_user = os.environ["NEO4J_USER"]
            n4j_password = os.environ["NEO4J_PASSWORD"]
        except KeyError:
            print(
                "Please set the environment variables NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD"
            )
            return

        start_time = time.time()
        BATCH_SIZE = 1000
        df = self.csv_manager.get_dataframe()

        # Get unique start and end node information
        unique_starts = df[
            ["CustomerID", "start_vertex_type", "Name", "Address", "Email", "Phone"]
        ].drop_duplicates()
        unique_ends = df[
            ["ProductID", "end_vertex_type", "SKU", "Price", "Color", "Size", "Weight"]
        ].drop_duplicates()

        start_label = unique_starts.iloc[0]["start_vertex_type"]
        end_label = unique_ends.iloc[0]["end_vertex_type"]

        async with AsyncGraphDatabase.driver(
            n4j_uri, auth=(n4j_user, n4j_password)
        ) as driver:
            async with driver.session() as session:
                # Clear the database
                await session.run("MATCH (a)-[r]->() DELETE a, r")
                await session.run("MATCH (a) DELETE a")
                # Manage indices
                await session.run(f"DROP INDEX {start_label}_index_id IF EXISTS")
                await session.run(f"DROP INDEX {end_label}_index_id IF EXISTS")
                await session.run(
                    f"CREATE INDEX {start_label}_index_id FOR (n:{start_label}) ON (n.CustomerID)"
                )
                await session.run(
                    f"CREATE INDEX {end_label}_index_id FOR (n:{end_label}) ON (n.ProductID)"
                )

                # Create start nodes in batches
                for idx in range(0, len(unique_starts), BATCH_SIZE):
                    batch = unique_starts.iloc[idx : idx + BATCH_SIZE]
                    starts = [
                        {
                            start_label: row["start_vertex_type"],
                            "CustomerID": row["CustomerID"],
                            "Name": row["Name"],
                            "Address": row["Address"],
                            "Email": row["Email"],
                            "Phone": row["Phone"],
                        }
                        for _, row in batch.iterrows()
                    ]
                    query = (
                        f"UNWIND $starts AS row "
                        f"CREATE (a:{start_label} {{CustomerID: row.CustomerID, Name: row.Name, "
                        f"Address: row.Address, Email: row.Email, Phone: row.Phone}}) "
                        f"SET a += row"
                    )
                    await session.run(query, starts=starts)

                # Create end nodes in batches
                for idx in range(0, len(unique_ends), BATCH_SIZE):
                    batch = unique_ends.iloc[idx : idx + BATCH_SIZE]
                    ends = [
                        {
                            end_label: row["end_vertex_type"],
                            "ProductID": row["ProductID"],
                            "SKU": row["SKU"],
                            "Price": row["Price"],
                            "Color": row["Color"],
                            "Size": row["Size"],
                            "Weight": row["Weight"],
                        }
                        for _, row in batch.iterrows()
                    ]
                    query = (
                        f"UNWIND $ends AS row "
                        f"CREATE (f:{end_label} {{ProductID: row.ProductID, SKU: row.SKU, "
                        f"Price: row.Price, Color: row.Color, Size: row.Size, Weight: row.Weight}}) "
                        f"SET f += row"
                    )
                    await session.run(query, ends=ends)

                # Create edges in batches
                for idx in range(0, len(df), BATCH_SIZE):
                    batch = df.iloc[idx : idx + BATCH_SIZE]
                    edges = [
                        {"from": row["CustomerID"], "to": row["ProductID"]}
                        for _, row in batch.iterrows()
                    ]
                    query = (
                        f"UNWIND $edges AS row "
                        f"MATCH (from:{start_label} {{CustomerID: row.from}}) "
                        f"MATCH (to:{end_label} {{ProductID: row.to}}) "
                        f"CREATE (from)-[r:BOUGHT]->(to) "
                        f"SET r += row"
                    )
                    await session.run(query, edges=edges)
        self._show_time(start_time, sys._getframe().f_code.co_name)

    @staticmethod
    def _show_time(start_time: float, message: str) -> None:
        elapsed = time.time() - start_time if start_time else 0.0
        print(f"Time for {message}: {elapsed:.2f} seconds")


class PgsqlLoader:
    """
    Load CSV data into PostgreSQL.
    """

    import psycopg as pg

    def __init__(self, csv_manager: CsvDataManager) -> None:
        self.csv_manager = csv_manager

    async def load_data(self) -> None:
        log.info("Loading CSV to PGSQL")
        try:
            con_string = os.environ["SRC_PG_CONNECTION_STRING"]
        except KeyError:
            print("Please set the environment variable SRC_PG_CONNECTION_STRING")
            return

        start_time = time.time()
        schema = "public"
        src_tables = {"start": "Customer", "end": "Product", "edges": "BOUGHT"}

        df = self.csv_manager.get_dataframe()

        # Prepare data and types for each table
        data_frames = [None, None, None]
        types = [None, None, None]

        # Start table (Customer)
        data_frames[0] = df[
            ["CustomerID", "Name", "Address", "Email", "Phone"]
        ].drop_duplicates()
        data_frames[0].insert(0, "CustomerSerial", range(1, len(data_frames[0]) + 1))
        types[0] = ["SERIAL", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT"]

        # End table (Product)
        data_frames[1] = df[
            ["ProductID", "Phrase", "SKU", "Price", "Color", "Size", "Weight"]
        ].drop_duplicates()
        data_frames[1].insert(0, "ProductSerial", range(1, len(data_frames[1]) + 1))
        types[1] = ["SERIAL", "TEXT", "TEXT", "TEXT", "REAL", "TEXT", "TEXT", "INT"]

        # Edges table (BOUGHT)
        data_frames[2] = df[["CustomerID", "ProductID"]].copy()
        data_frames[2].insert(0, "BoughtSerial", range(1, len(data_frames[2]) + 1))
        types[2] = ["SERIAL", "TEXT", "TEXT"]

        with pg.connect(con_string) as conn:
            with conn.cursor() as cur:
                for (table_key, table_name), df_data, col_types in zip(
                    src_tables.items(), data_frames, types
                ):
                    cur.execute(f'DROP TABLE IF EXISTS {schema}."{table_name}"')
                    columns = ", ".join(
                        [f'"{col}" {tp}' for col, tp in zip(df_data.columns, col_types)]
                    )
                    cur.execute(f'CREATE TABLE {schema}."{table_name}" ({columns})')
                    query = (
                        f'COPY {schema}."{table_name}" FROM STDIN (FORMAT TEXT, FREEZE)'
                    )
                    with cur.copy(query) as copy:
                        copy_data = "\n".join(
                            "\t".join(map(str, row))
                            for row in df_data.itertuples(index=False)
                        )
                        copy.write(copy_data)
                    # Create indexes based on table type
                    if table_key == "edges":
                        cur.execute(
                            f'CREATE INDEX ON {schema}."{table_name}"("CustomerID")'
                        )
                        cur.execute(
                            f'CREATE INDEX ON {schema}."{table_name}"("ProductID")'
                        )
                    elif table_key == "start":
                        cur.execute(
                            f'CREATE INDEX ON {schema}."{table_name}"("CustomerID")'
                        )
                    elif table_key == "end":
                        cur.execute(
                            f'CREATE INDEX ON {schema}."{table_name}"("ProductID")'
                        )
                cur.execute("COMMIT")
        self._show_time(start_time, sys._getframe().f_code.co_name)

    @staticmethod
    def _show_time(start_time: float, message: str) -> None:
        elapsed = time.time() - start_time if start_time else 0.0
        print(f"Time for {message}: {elapsed:.2f} seconds")


class CosmosGremlinLoader:
    """
    Load CSV data into Cosmos DB using the Gremlin API.
    """

    from gremlin_python.driver import client, serializer

    def __init__(self, csv_manager: CsvDataManager) -> None:
        self.csv_manager = csv_manager

    def execute_gremlin_query(self, g_client: client.Client, query: str) -> None:
        """
        Execute a Gremlin query with retry logic.
        """
        retries = 0
        initial_wait = 1
        while retries < 5:
            try:
                future = g_client.submitAsync(query)
                result = future.result()
                log.debug(f"Gremlin query result: {result.all().result()}")
                return
            except Exception as e:
                wait_time = initial_wait * (2**retries)
                log.warning(
                    f"Query failed (attempt {retries + 1}). Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
                retries += 1
        raise Exception("Max retries exceeded for Gremlin query")

    async def load_data(self) -> None:
        log.info("Loading CSV to Cosmos DB via Gremlin API")
        try:
            cosmos_gremlin_endpoint = os.environ["COSMOS_GREMLIN_ENDPOINT"]
            cosmos_gremlin_key = os.environ["COSMOS_GREMLIN_KEY"]
        except KeyError:
            print(
                "Please set the environment variables COSMOS_GREMLIN_ENDPOINT and COSMOS_GREMLIN_KEY"
            )
            raise

        start_time = time.time()
        COSMOS_USERNAME = "/dbs/db1/colls/transaction"
        COSMOS_PKEY = "pk"

        LOGICAL_PARTITION_SIZE = 20 * 1024 * 1024 * 1024  # 20GB
        AVERAGE_SIZE_OF_DOCUMENT = 512  # 512 bytes
        num_of_docs_per_partition = LOGICAL_PARTITION_SIZE // AVERAGE_SIZE_OF_DOCUMENT
        num_of_pk = 1
        MAX_OPERATOR_DEPTH = 400

        try:
            g_client = client.Client(
                url=cosmos_gremlin_endpoint,
                traversal_source="g",
                username=COSMOS_USERNAME,
                password=cosmos_gremlin_key,
                message_serializer=serializer.GraphSONSerializersV2d0(),
                timeout=600,
            )
        except Exception as e:
            print(f"Failed to connect to Gremlin server: {e}")
            return

        df = self.csv_manager.get_dataframe()
        df.drop_duplicates(inplace=True)

        vertex_columns: Dict[str, Any] = {
            "Customer": ["CustomerID", "Name", "Address", "Email", "Phone"],
            "Product": [
                "ProductID",
                "Phrase",
                "SKU",
                "Price",
                "Color",
                "Size",
                "Weight",
            ],
        }

        total_docs = 0
        max_workers = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for vertex_type, cols in vertex_columns.items():
                vertices = df[cols].drop_duplicates()
                # Escape single quotes in string fields
                vertices = vertices.applymap(
                    lambda x: x.replace("'", r"\'") if isinstance(x, str) else x
                )
                if vertex_type == "Customer":
                    tmp_query = """.addV('Customer')
                        .property('Name', '{Name}')
                        .property('CustomerID', '{CustomerID}')
                        .property('Address', '{Address}')
                        .property('Email', '{Email}')
                        .property('Phone', '{Phone}')
                        .property('{pk}', '{num_of_pk}')"""
                elif vertex_type == "Product":
                    tmp_query = """.addV('Product')
                        .property('Phrase', '{Phrase}')
                        .property('ProductID', '{ProductID}')
                        .property('SKU', '{SKU}')
                        .property('Price', '{Price}')
                        .property('Color', '{Color}')
                        .property('Size', '{Size}')
                        .property('Weight', '{Weight}')
                        .property('{pk}', '{num_of_pk}')"""
                chunk_size = int(MAX_OPERATOR_DEPTH / (len(cols) + 2))
                for i, chunk in enumerate(
                    CsvDataManager.get_chunks(vertices, chunk_size)
                ):
                    log.info(
                        f"Creating '{vertex_type}' vertices: {len(chunk)} records."
                    )
                    if len(chunk.columns) == 5:
                        query = "g" + "".join(
                            [
                                tmp_query.format(
                                    Name=row["Name"],
                                    CustomerID=row["CustomerID"],
                                    Address=row["Address"],
                                    Email=row["Email"],
                                    Phone=row["Phone"],
                                    pk=COSMOS_PKEY,
                                    num_of_pk=num_of_pk,
                                )
                                for _, row in chunk.iterrows()
                            ]
                        )
                    elif len(chunk.columns) == 7:
                        query = "g" + "".join(
                            [
                                tmp_query.format(
                                    Phrase=row["Phrase"],
                                    ProductID=row["ProductID"],
                                    SKU=row["SKU"],
                                    Price=row["Price"],
                                    Color=row["Color"],
                                    Size=row["Size"],
                                    Weight=row["Weight"],
                                    pk=COSMOS_PKEY,
                                    num_of_pk=num_of_pk,
                                )
                                for _, row in chunk.iterrows()
                            ]
                        )
                    futures.append(
                        executor.submit(self.execute_gremlin_query, g_client, query)
                    )
                    total_docs += len(chunk)
                    if total_docs % num_of_docs_per_partition == 0:
                        num_of_pk += 1
            concurrent.futures.wait(futures)

        # Create edges (BOUGHT relationships) using a larger thread pool
        max_workers = 1024
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, row in enumerate(df.itertuples(index=False), start=1):
                log.info(f"Creating 'BOUGHT' edge: {i}")
                edge_query = (
                    f"g.V().has('CustomerID', '{row.CustomerID}')"
                    f".addE('BOUGHT').to(g.V().has('ProductID', '{row.ProductID}'))"
                )
                futures.append(
                    executor.submit(self.execute_gremlin_query, g_client, edge_query)
                )
            concurrent.futures.wait(futures)

        g_client.close()
        self._show_time(start_time, sys._getframe().f_code.co_name)

    @staticmethod
    def _show_time(start_time: float, message: str) -> None:
        elapsed = time.time() - start_time if start_time else 0.0
        print(f"Time for {message}: {elapsed:.2f} seconds")
