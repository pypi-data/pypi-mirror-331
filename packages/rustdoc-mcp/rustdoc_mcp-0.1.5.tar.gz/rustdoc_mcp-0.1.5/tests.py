#!/usr/bin/env python3
"""
Simple test script for rustdoc-mcp server

Before running this script, make sure to install the required dependencies:
    pip install mcp
"""

import os
import sys
import json
import asyncio
import argparse

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: Required dependency 'mcp' not found.")
    print("Please install it using: pip install mcp")
    sys.exit(1)

async def test_standard_lib(session):
    """Test standard library documentation"""
    print("\n=== Testing Standard Library Documentation ===")
    paths = [
        "std::vec::Vec",
        "std::collections::HashMap",
        "std::option::Option",
        "std::result::Result",
        "std::string::String",
    ]
    
    for path in paths:
        print(f"\nGetting documentation for {path}...")
        try:
            result = await session.call_tool(
                "get_doc", 
                arguments={"path": path}
            )
            
            # Check the response
            content = result.content
            if content and isinstance(content, list) and len(content) > 0:
                text = content[0].text if hasattr(content[0], 'text') else str(content[0])
                
                # Try to parse JSON if it looks like JSON
                if text.startswith('{') and '"content":' in text:
                    try:
                        # This is double-encoded JSON, let's parse it for better display
                        parsed = json.loads(text)
                        if 'content' in parsed and len(parsed['content']) > 0:
                            inner_text = parsed['content'][0].get('text', '')
                            text = inner_text
                    except json.JSONDecodeError:
                        # If we can't parse it, just use the original text
                        pass
                        
                # Print a short preview
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"✅ Success ({len(text)} characters)")
                print(f"Preview: {preview}")
            else:
                print(f"❌ Failed: Empty response")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_cache(session):
    """Test cache functionality"""
    print("\n=== Testing Cache Functionality ===")
    
    # First call should be a cache miss
    path = "std::vec::Vec"
    print(f"First call to {path} (should be cache miss)...")
    await session.call_tool("get_doc", arguments={"path": path})
    
    # Get cache stats
    print("\nChecking cache stats...")
    stats_result = await session.call_tool("cache_stats")
    stats_text = stats_result.content[0].text if hasattr(stats_result.content[0], 'text') else str(stats_result.content[0])
    
    # Try to parse JSON if it looks like JSON
    if stats_text.startswith('{') and ':' in stats_text:
        try:
            stats = json.loads(stats_text)
            # Check if this is a nested JSON structure
            if isinstance(stats, dict) and 'content' in stats:
                inner_text = stats['content'][0].get('text', '{}')
                stats = json.loads(inner_text)
        except json.JSONDecodeError:
            # If parsing fails, use the original
            stats = {'text': stats_text}
    else:
        stats = {'text': stats_text}
        
    print(f"Cache stats: {stats}")
    
    # Second call should be a cache hit
    print(f"\nSecond call to {path} (should be cache hit)...")
    await session.call_tool("get_doc", arguments={"path": path})
    
    # Get updated cache stats
    print("\nChecking updated cache stats...")
    stats_result = await session.call_tool("cache_stats")
    stats_text = stats_result.content[0].text if hasattr(stats_result.content[0], 'text') else str(stats_result.content[0])
    
    # Try to parse JSON if it looks like JSON
    if stats_text.startswith('{') and ':' in stats_text:
        try:
            stats = json.loads(stats_text)
            # Check if this is a nested JSON structure
            if isinstance(stats, dict) and 'content' in stats:
                inner_text = stats['content'][0].get('text', '{}')
                stats = json.loads(inner_text)
        except json.JSONDecodeError:
            # If parsing fails, use the original
            stats = {'text': stats_text}
    else:
        stats = {'text': stats_text}
        
    print(f"Updated cache stats: {stats}")
    
    # Clear cache
    print("\nClearing cache...")
    clear_result = await session.call_tool("clear_cache")
    response_text = clear_result.content[0].text if hasattr(clear_result.content[0], 'text') else str(clear_result.content[0])
    
    # Try to parse JSON if it looks like JSON
    if response_text.startswith('{') and '"content":' in response_text:
        try:
            parsed = json.loads(response_text)
            if 'content' in parsed and len(parsed['content']) > 0:
                response_text = parsed['content'][0].get('text', response_text)
        except json.JSONDecodeError:
            pass
            
    print(f"Response: {response_text}")

async def test_external_crate(session, crate_name):
    """Test external crate documentation"""
    print(f"\n=== Testing External Crate: {crate_name} ===")
    
    print(f"Getting documentation for {crate_name}...")
    try:
        result = await session.call_tool(
            "get_doc", 
            arguments={"path": crate_name}
        )
        
        # Check the response
        content = result.content
        if content and isinstance(content, list) and len(content) > 0:
            text = content[0].text if hasattr(content[0], 'text') else str(content[0])
            
            # Try to parse JSON if it looks like JSON
            if text.startswith('{') and '"content":' in text:
                try:
                    # This is double-encoded JSON, let's parse it for better display
                    parsed = json.loads(text)
                    if 'content' in parsed and len(parsed['content']) > 0:
                        inner_text = parsed['content'][0].get('text', '')
                        text = inner_text
                except json.JSONDecodeError:
                    # If we can't parse it, just use the original text
                    pass
                    
            # Print a short preview
            preview = text[:200] + "..." if len(text) > 200 else text
            print(f"✅ Success ({len(text)} characters)")
            print(f"Preview: {preview}")
        else:
            print(f"❌ Failed: Empty response")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

async def test_list_tools(session):
    """Test listing available tools"""
    print("\n=== Testing Tool Listing ===")
    
    try:
        tools_result = await session.list_tools()
        # MCP returns a list of tools
        tools = tools_result.tools if hasattr(tools_result, 'tools') else []
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            description = tool.description.split('.')[0] if tool.description else "No description"
            print(f"- {tool.name}: {description}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description="Test the rustdoc-mcp server")
    parser.add_argument("--command", default="python -m rustdoc_mcp.main", 
                      help="Command to run the server (default: python -m rustdoc_mcp.main)")
    parser.add_argument("--external-crate", default="serde",
                      help="External crate to test (default: serde)")
    args = parser.parse_args()
    
    print("Starting test for rustdoc-mcp server...")
    print(f"Server command: {args.command}")
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command=args.command.split()[0],
        args=args.command.split()[1:],
        env=os.environ.copy()
    )
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("Connected to server successfully!")
                
                # Run tests
                await test_list_tools(session)
                await test_standard_lib(session)
                await test_cache(session)
                await test_external_crate(session, args.external_crate)
                
                print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))