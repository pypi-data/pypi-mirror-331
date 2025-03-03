from aiohttp import web
import asyncio
import fire
import json

def make_rpc_server(base_url: str, cmd_entry, secret = None,
                    auth_header='X-Auth-Token', json_dumps=json.dumps):
    async def handler(request: web.Request) -> web.Response:
        try:
            if secret is not None:
                auth_token = request.headers.get(auth_header)
                if auth_token != secret:
                    return web.json_response({'error': 'unauthorized'}, status=401)
            data = await request.json()
            args = data.get('args')
            if args is None:
                return web.json_response({'error': 'args not found'}, status=400)
            if not isinstance(args, list):
                return web.json_response({'error': 'args must be a list'}, status=400)
            ret = fire.Fire(cmd_entry, args)
            res = {'result': ret}
            return web.json_response(res, dumps=json_dumps)

        except (Exception, SystemExit) as e:
            return web.json_response({'error': str(e)}, status=400)

    app = web.Application()
    app.add_routes([web.post(base_url, handler)])
    return app


def start_rpc_server(base_url: str, cmd_entry, secret=None, json_dumps=json.dumps,
                     host='localhost', port=8000, auth_header='X-Auth-Token'):
    loop = asyncio.new_event_loop()
    app = make_rpc_server(base_url, cmd_entry, secret=secret, auth_header=auth_header, json_dumps=json_dumps)
    web.run_app(app, loop=loop, host=host, port=port)


def make_fire_cmd(cmd_entry, json_dumps=json.dumps):
    def fire_cmd(base_url: str, secret=None, host='localhost', port=8000, auth_header='X-Auth-Token'):
        start_rpc_server(base_url, cmd_entry,
                         secret=secret, json_dumps=json_dumps,
                         host=host, port=port, auth_header=auth_header)
    return fire_cmd
