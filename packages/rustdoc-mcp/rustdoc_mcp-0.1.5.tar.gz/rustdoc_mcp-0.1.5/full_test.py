#!/usr/bin/env python3
"""
Test script for rustdoc-mcp server that saves full output to files

This script:
1. Tests all the standard library types
2. Saves complete output to individual files
3. Properly handles external crate documentation
"""

import os
import sys
import json
import asyncio
import argparse
import time
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: Required dependency 'mcp' not found.")
    print("Please install it using: pip install mcp")
    sys.exit(1)

class RustDocTester:
    """Class for testing the rustdoc-mcp server and saving results"""
    
    def __init__(self):
        self.output_dir = Path("./rustdoc_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create timestamped directory for this test run
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.output_dir / timestamp
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def test_and_save(self, session, path, filename=None):
        """Test a documentation path and save the full output to a file"""
        if filename is None:
            # Replace :: with _ for filename
            filename = path.replace("::", "_").replace(".", "_") + ".md"
        
        output_path = self.output_dir / filename
        print(f"Getting documentation for {path}...")
        
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
                
                # Save the full text to file
                with open(output_path, 'w') as f:
                    f.write(text)
                    
                # Print a short preview and success message
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"✅ Success ({len(text)} characters), saved to {output_path}")
                print(f"Preview: {preview}")
                return text
            else:
                error_msg = f"❌ Failed: Empty response"
                print(error_msg)
                with open(output_path, 'w') as f:
                    f.write(error_msg)
                return None
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(error_msg)
            with open(output_path, 'w') as f:
                f.write(error_msg)
            return None

    async def test_standard_lib(self, session):
        """Test standard library documentation"""
        print("\n=== Testing Standard Library Documentation ===")
        paths = [
            "std::vec::Vec",
            "std::collections::HashMap",
            "std::option::Option",
            "std::result::Result",
            "std::string::String",
            "std::fs::File",
            "std::sync::Mutex",
        ]
        
        for path in paths:
            await self.test_and_save(session, path)

    async def test_external_crate(self, session, crate_name, with_features=None, project_path=None):
        """Test external crate documentation with proper feature handling"""
        print(f"\n=== Testing External Crate: {crate_name} ===")
        
        # Construct arguments with features if specified
        args = {"path": crate_name}
        if with_features:
            args["flags"] = ["--features", with_features]
        
        # If a project path is specified, include it in the arguments
        if project_path:
            print(f"Using project path: {project_path}")
            args["project_path"] = project_path
        
        output_path = self.output_dir / f"{crate_name}.md"
        
        try:
            print(f"Getting documentation for {crate_name}" + 
                  (f" with features: {with_features}" if with_features else "") + 
                  "...")
            
            result = await session.call_tool("get_doc", arguments=args)
            
            # Check the response
            content = result.content
            if content and isinstance(content, list) and len(content) > 0:
                text = content[0].text if hasattr(content[0], 'text') else str(content[0])
                
                # Try to parse JSON if it looks like JSON
                if text.startswith('{') and '"content":' in text:
                    try:
                        parsed = json.loads(text)
                        if 'content' in parsed and len(parsed['content']) > 0:
                            inner_text = parsed['content'][0].get('text', '')
                            text = inner_text
                    except json.JSONDecodeError:
                        pass
                
                # Save the full text to file
                with open(output_path, 'w') as f:
                    f.write(text)
                    
                # Print a short preview
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"✅ Success ({len(text)} characters), saved to {output_path}")
                print(f"Preview: {preview}")
                
                # If we failed to find the crate but found other generated docs,
                # try checking one of those
                if "but documentation was generated for:" in text:
                    # Extract the suggested crate name
                    parts = text.split("but documentation was generated for:")
                    if len(parts) > 1:
                        suggested_crates = parts[1].strip().split(", ")
                        if suggested_crates:
                            suggested = suggested_crates[0].strip()
                            print(f"Trying suggested crate: {suggested}")
                            await self.test_and_save(session, suggested, f"{crate_name}_suggested.md")
                
                return text
            else:
                error_msg = f"❌ Failed: Empty response"
                print(error_msg)
                with open(output_path, 'w') as f:
                    f.write(error_msg)
                return None
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(error_msg)
            with open(output_path, 'w') as f:
                f.write(error_msg)
            return None

    async def test_local_project(self, session, local_path):
        """Test documentation for a local Rust file or module"""
        if not os.path.exists(local_path):
            print(f"❌ Error: Local path {local_path} does not exist")
            return
            
        print(f"\n=== Testing Local Project: {local_path} ===")
        
        # Use absolute path
        abs_path = os.path.abspath(local_path)
        await self.test_and_save(session, abs_path, "local_" + os.path.basename(local_path) + ".md")

    async def test_fixing_serde(self, session, project_path=None):
        """Special test to fix serde documentation issues"""
        print("\n=== Special Test for Serde Crate ===")
        
        # Different approaches to try with serde
        approaches = [
            # Try with a specific path to a module or type
            {"path": "serde::ser::Serializer"},
            {"path": "serde::de::Deserializer"},
            {"path": "serde::Serialize"},
            {"path": "serde::Deserialize"},
            # Try with different flags
            {"path": "serde", "flags": ["--document-private-items"]},
            {"path": "serde", "flags": ["--no-deps"]},
        ]
        
        # Add project path to each approach if provided
        if project_path:
            print(f"Using project path for serde tests: {project_path}")
            for approach in approaches:
                approach["project_path"] = project_path
        
        for i, args in enumerate(approaches):
            print(f"\nTrying approach {i+1} for serde: {args}")
            try:
                result = await session.call_tool("get_doc", arguments=args)
                
                # Check the response
                content = result.content
                if content and isinstance(content, list) and len(content) > 0:
                    text = content[0].text if hasattr(content[0], 'text') else str(content[0])
                    
                    # Try to parse JSON if it looks like JSON
                    if text.startswith('{') and '"content":' in text:
                        try:
                            parsed = json.loads(text)
                            if 'content' in parsed and len(parsed['content']) > 0:
                                inner_text = parsed['content'][0].get('text', '')
                                text = inner_text
                        except json.JSONDecodeError:
                            pass
                    
                    # Save to file
                    filename = f"serde_approach_{i+1}.md"
                    output_path = self.output_dir / filename
                    with open(output_path, 'w') as f:
                        f.write(text)
                    
                    # Print a short preview
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"✅ Result from approach {i+1} ({len(text)} characters), saved to {output_path}")
                    print(f"Preview: {preview}")
            except Exception as e:
                print(f"❌ Error with approach {i+1}: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description="Test the rustdoc-mcp server and save full output")
    parser.add_argument("--command", default="python -m rustdoc_mcp.main", 
                      help="Command to run the server (default: python -m rustdoc_mcp.main)")
    parser.add_argument("--external-crates", default="serde,tokio,axum,rand",
                      help="Comma-separated list of external crates to test (default: serde,tokio,axum,rand)")
    parser.add_argument("--fix-serde", action="store_true",
                      help="Run special tests to troubleshoot serde documentation")
    parser.add_argument("--local-path", 
                      help="Local Rust file or module to test")
    parser.add_argument("--project-path",
                      help="Path to a Rust project containing documentation for the crates")
    args = parser.parse_args()
    
    # Create tester instance
    tester = RustDocTester()
    output_dir_abs = os.path.abspath(tester.output_dir)
    
    print(f"Starting full test for rustdoc-mcp server...")
    print(f"Output will be saved to: {output_dir_abs}")
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
                await tester.test_standard_lib(session)
                
                # Test external crates
                external_crates = args.external_crates.split(",")
                for crate in external_crates:
                    await tester.test_external_crate(session, crate.strip(), project_path=args.project_path)
                
                # Special serde test if requested
                if args.fix_serde:
                    await tester.test_fixing_serde(session, project_path=args.project_path)
                
                # Test local project if requested
                if args.local_path:
                    await tester.test_local_project(session, args.local_path)
                
                print(f"\n✅ All tests completed! Output saved to {output_dir_abs}")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))