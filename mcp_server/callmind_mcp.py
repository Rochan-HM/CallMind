#!/usr/bin/env python3
import asyncio
import json
import os
import logging
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaCloudMCPServer:
    def __init__(self):
        self.server = Server("chroma-cloud-server")
        self.client: Optional[chromadb.ClientAPI] = None
        self.collection = None
        
        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
    
    async def initialize_chroma_client(self, api_key: str, tenant: str = "default", database: str = "default"):
        """Initialize connection to Chroma Cloud"""
        try:
            self.client = chromadb.CloudClient(
                tenant=tenant,
                database=database,
                api_key=api_key
            )
            logger.info("Successfully connected to Chroma Cloud")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Chroma Cloud: {e}")
            return False
    
    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools"""
        tools = [
            Tool(
                name="query_collection",
                description="Query a Chroma collection with text or vector similarity search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to query"
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Text to search for (will be embedded automatically)"
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 10
                        },
                        "where": {
                            "type": "object",
                            "description": "Optional metadata filter conditions"
                        },
                        "include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to include in results: documents, metadatas, distances",
                            "default": ["documents", "metadatas", "distances"]
                        }
                    },
                    "required": ["collection_name", "query_text"]
                }
            ),
            Tool(
                name="list_collections",
                description="List all available collections in the Chroma database",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_collection_info",
                description="Get information about a specific collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to get info for"
                        }
                    },
                    "required": ["collection_name"]
                }
            ),
            Tool(
                name="connect_chroma",
                description="Initialize connection to Chroma Cloud",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "api_key": {
                            "type": "string",
                            "description": "Chroma Cloud API key"
                        },
                        "tenant": {
                            "type": "string",
                            "description": "Tenant name",
                            "default": "default"
                        },
                        "database": {
                            "type": "string",
                            "description": "Database name",
                            "default": "default"
                        }
                    },
                    "required": ["api_key"]
                }
            )
        ]
        
        return ListToolsResult(tools=tools)
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        try:
            if request.params.name == "connect_chroma":
                return await self._connect_chroma(request.params.arguments)
            elif request.params.name == "query_collection":
                return await self._query_collection(request.params.arguments)
            elif request.params.name == "list_collections":
                return await self._list_collections()
            elif request.params.name == "get_collection_info":
                return await self._get_collection_info(request.params.arguments)
            else:
                raise ValueError(f"Unknown tool: {request.params.name}")
                
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True
            )
    
    async def _connect_chroma(self, args: Dict[str, Any]) -> CallToolResult:
        """Connect to Chroma Cloud"""
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT")
        database = args.get("database", "default")
        
        if not api_key:
            raise ValueError("API key is required")
        
        success = await self.initialize_chroma_client(api_key, tenant, database)
        
        if success:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Successfully connected to Chroma Cloud (tenant: {tenant}, database: {database})"
                )]
            )
        else:
            raise Exception("Failed to connect to Chroma Cloud")
    
    async def _query_collection(self, args: Dict[str, Any]) -> CallToolResult:
        """Query a Chroma collection"""
        if not self.client:
            raise Exception("Not connected to Chroma Cloud. Use connect_chroma first.")
        
        collection_name = args.get("collection_name")
        query_text = args.get("query_text")
        n_results = args.get("n_results", 10)
        where = args.get("where")
        include = args.get("include", ["documents", "metadatas", "distances"])
        
        if not collection_name or not query_text:
            raise ValueError("collection_name and query_text are required")
        
        try:
            collection = self.client.get_collection(name=collection_name)
            
            # Perform the query
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                include=include
            )
            
            # Format results for better readability
            formatted_results = []
            for i in range(len(results.get('ids', [[]])[0])):
                result_item = {
                    'id': results['ids'][0][i] if 'ids' in results else None,
                }
                
                if 'documents' in include and 'documents' in results:
                    result_item['document'] = results['documents'][0][i]
                
                if 'metadatas' in include and 'metadatas' in results:
                    result_item['metadata'] = results['metadatas'][0][i]
                
                if 'distances' in include and 'distances' in results:
                    result_item['distance'] = results['distances'][0][i]
                
                formatted_results.append(result_item)
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=json.dumps({
                        "query": query_text,
                        "collection": collection_name,
                        "results_count": len(formatted_results),
                        "results": formatted_results
                    }, indent=2)
                )]
            )
            
        except Exception as e:
            raise Exception(f"Query failed: {str(e)}")
    
    async def _list_collections(self) -> CallToolResult:
        """List all collections"""
        if not self.client:
            raise Exception("Not connected to Chroma Cloud. Use connect_chroma first.")
        
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "collections": collection_names,
                        "count": len(collection_names)
                    }, indent=2)
                )]
            )
        except Exception as e:
            raise Exception(f"Failed to list collections: {str(e)}")
    
    async def _get_collection_info(self, args: Dict[str, Any]) -> CallToolResult:
        """Get information about a collection"""
        if not self.client:
            raise Exception("Not connected to Chroma Cloud. Use connect_chroma first.")
        
        collection_name = args.get("collection_name")
        if not collection_name:
            raise ValueError("collection_name is required")
        
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "name": collection_name,
                        "count": count,
                        "metadata": collection.metadata
                    }, indent=2)
                )]
            )
        except Exception as e:
            raise Exception(f"Failed to get collection info: {str(e)}")

async def main():
    """Main entry point for the MCP server"""
    server_instance = ChromaCloudMCPServer()
    
    # Run the server
    async with stdio_server(server_instance.server) as streams:
        await server_instance.server.run(
            streams[0], streams[1], InitializationOptions(
                server_name="chroma-cloud-server",
                server_version="1.0.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())