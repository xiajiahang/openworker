import asyncio, json, sys, html
from pathlib import Path
from types import SimpleNamespace
from coworker.mcp.config import MCPServerDef
from coworker.mcp.tools import build_callables
from coworker.tools.registry import ToolRegistry

async def main():
    server = MCPServerDef(name='hub-gmail-thresholdstack', transport='http', url='https://example.com/mcp')
    remote_names = ['gmail-thresholdstack__get_gmail_message_content', 'gmail-thresholdstack__get_gmail_messages_content_batch']
    async def call(remote, args):
        return {'remote_tool': remote, 'message_id': args['message_id']}
    funcs = build_callables(server, [SimpleNamespace(name=n, description='Read messages', inputSchema={'type':'object', 'properties':{}}) for n in remote_names], call, asyncio.get_running_loop())
    registry = ToolRegistry()
    registry.register_all(funcs)
    results = []
    for remote in remote_names:
        full = f'mcp__{server.name}__{remote}'
        try:
            result = await asyncio.to_thread(registry.execute, full, {'message_id':'123'})
        except KeyError as error:
            result = {'error':str(error)}
        results.append({'full_name':full, 'result':result})
    output = {'source_commit':'7e20213', 'server':server.name, 'offered_tools':len(remote_names), 'registered_tools':len(registry.names()), 'schema_names':registry.names(), 'calls':results}
    dest = Path(sys.argv[1]); stage=sys.argv[2]
    (dest / f'{stage}.json').write_text(json.dumps(output, indent=2))
    (dest / f'{stage}.html').write_text('<!doctype html><meta charset="utf-8"><title>MCP name reproduction</title><style>body{margin:40px;font:16px system-ui;background:#f5f5f5;color:#222}pre{padding:24px;background:white;border:1px solid #ccc;font:14px/1.6 monospace;white-space:pre-wrap;overflow-wrap:anywhere}h1{font-size:26px}</style><h1>OpenWorker #746 — '+stage+'</h1><p>Output from the real MCP wrapper and ToolRegistry; local async echo transport, no external credentials.</p><pre>'+html.escape(json.dumps(output,indent=2))+'</pre>')
    print(json.dumps(output, indent=2))
asyncio.run(main())
