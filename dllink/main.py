from typing import Any, Dict
import websockets
import threading
import asyncio
import time
import json
import sys
from dataclasses import dataclass

class Reporter:
    @classmethod
    def error_addr(cls):
        print("< 没有目标地址")

@dataclass
class RecvRemotePacket:
    from_addr: str
    to_addr: str
    data: str

@dataclass
class RouteTableItem:
    remote_ip: str
    remote_port: int

class ModuleSender:
    def __init__(self, manager, module_addr) -> None:
        self.manager = manager
        self.module_addr = module_addr # 模块自己的地址

    async def send(self, data: str, addr: str):
        # data是仅仅是要发的数据
        # 在这里构造packet,如果需要拆包也在这里
        packet = RecvRemotePacket(
            from_addr = self.module_addr,
            to_addr = addr,
            data = data
        )

        # logger.print()后进入这里，addr是虚拟地址
        await self.manager.forward(packet)

class MyClient:
    _instence: Any = None
    @classmethod
    def get_instance(cls, *args, **kwargs):
        assert cls._instence is None or (len(args) == 0 and len(kwargs) == 0)
        if cls._instence is None:
            cls._instence = MyClient(*args, **kwargs)
        return cls._instence
    
    def __init__(self, addr_prefix: str=None, route_table: Dict[str, RouteTableItem]=None, *args, **kwargs) -> None:
        if route_table is None:
            route_table: Dict[str, RouteTableItem] = {}
        if addr_prefix is None:
            addr_prefix = self._generate_address_prefix()
        self.route_table = route_table
        self.addr_prefix = 'client' + addr_prefix
        self.links = {}

    async def run_coroutine(self, ip):
        while True:
            try:
                async with websockets.connect(ip) as websocket:
                    print(f"Connected to {ip}")

                    remote_ip, remote_port = websocket.remote_address

                    # setup link info
                    self.links.setdefault(
                        (remote_ip, str(remote_port)), 
                        websocket
                    )

                    await self.say_hello(websocket, 'connecting server')

                    while True:
                        async for message in websocket: 
                            # 解包
                            packet = RecvRemotePacket(**json.loads(message.replace("'",'"')))

                            self.route_table.setdefault(
                                packet.from_addr, # 虚拟地址
                                (remote_ip, str(remote_port))# 对应的tcp/ip地址
                            )
                            
                            if packet.to_addr == self.addr_prefix: # 发给自己，而不是任何一个module
                                print(packet.data)
                            else:
                                # router_chain
                                await self.router_chain(packet)
            except:
                pass

    async def connect(self, ip_list):
        connections = [self.run_coroutine(ip) for ip in ip_list]
        await asyncio.gather(*connections)

    async def router_chain(self, packet: RecvRemotePacket):
        cs: CSManager = CSManager.get_instance()
        await cs.forward(packet)
    
    async def say_hello(self, socket, addr):
        packet = RecvRemotePacket(
            from_addr = self.addr_prefix,
            to_addr = addr,
            data = 'Hello'
        )
        await socket.send(str(packet.__dict__))

    def has_link(self, addr):
        if addr.split("/")[0] in self.route_table or addr in self.route_table:
            return True
        else:
            return False
        
    async def client_send(self, packet: RecvRemotePacket):
        addr = packet.to_addr
        to_ip = self.route_table.get(addr.split("/")[0])
        socket = self.links.get(to_ip, None)
        await socket.send(str(packet.__dict__))
        
    def _generate_address_prefix(self) -> str:
        return '0'

class MyServer:
    _instence: Any = None
    @classmethod
    def get_instance(cls, *args, **kwargs):
        assert cls._instence is None or (len(args) == 0 and len(kwargs) == 0)
        if cls._instence is None:
            cls._instence = MyServer(*args, **kwargs)
        return cls._instence
    
    def __init__(self, host: str=None, port: str=None, addr_prefix: str=None, route_table: Dict[str, RouteTableItem]=None, *args, **kwargs) -> None:
        if host is None:
            host = '127.0.0.1'
        if port is None:   
            port = '9876'
        if route_table is None:
            route_table: Dict[str, RouteTableItem] = {}
        if addr_prefix is None:
            addr_prefix = self._generate_address_prefix()
        self.host = host
        self.port = port
        self.route_table = route_table
        self.addr_prefix = 'server' + addr_prefix
        self.links = {}

    def _server_thread_worker(self):
        print("< Server launching...")
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        print(f"< Server started on {self.host}:{self.port}.")
        async def onRecv(socket, path): 

            # build connection
            remote_ip, remote_port = socket.remote_address

            # setup link info
            self.links.setdefault(
                (remote_ip, str(remote_port)), 
                socket
            )
                         
            async for message in socket: 

                # parse data
                packet = RecvRemotePacket(**json.loads(message.replace("'",'"')))

                self.route_table.setdefault(
                    packet.from_addr, # 虚拟地址
                    (remote_ip, str(remote_port))# 对应的tcp/ip地址
                )

                # router_chain
                await self.router_chain(packet)

            # unset link info
            self.links.pop((remote_ip, str(remote_port)))

        event_loop.run_until_complete(websockets.serve(onRecv, self.host, self.port))
        event_loop.run_forever()
    
    async def router_chain(self, packet: RecvRemotePacket):
        cs: CSManager = CSManager.get_instance()
        await cs.forward(packet)

    def has_link(self, addr):
        if addr.split("/")[0] in self.route_table or addr in self.route_table:
            return True
        else:
            return False
        
    async def server_send(self, packet: RecvRemotePacket):
        cs: CSManager = CSManager.get_instance()
        if packet.to_addr == 'connecting server':
            packet = RecvRemotePacket(
                from_addr = self.addr_prefix,
                to_addr = packet.from_addr,
                data = 'Hi!'
            )
            addr = packet.to_addr
            to_ip = self.route_table.get(addr)
            socket = self.links.get(to_ip, None)
            await socket.send(str(packet.__dict__))

        else:
            addr = packet.to_addr
            to_ip = self.route_table.get(addr.split("/")[0])
            socket = self.links.get(to_ip, None)
            await socket.send(str(packet.__dict__))

    def _generate_address_prefix(self) -> str:
        return '0'

class CSManager:
    _instence: Any = None

    def __init__(self, *args, **kwargs) -> None:
        self.client = MyClient.get_instance(*args, **kwargs)
        self.server = MyServer.get_instance(*args, **kwargs)
        self.routetable = {}
        self.functions = {}
        # sender = cs.register(self.on_recv, f'{cs.client.addr_prefix}/hello') 控制报文之类的

    @classmethod
    def get_instance(cls, *args, **kwargs):
        assert cls._instence is None or (len(args) == 0 and len(kwargs) == 0)
        if cls._instence is None:
            cls._instence = CSManager(*args, **kwargs)
        return cls._instence
    
    def register(self, on_recv_func, addr) -> ModuleSender:
        sender = ModuleSender(self, addr)
        self.functions.setdefault(addr, (on_recv_func, sender))
        return sender

    async def connect(self, ip_list):
        await self.client.connect(ip_list)

    async def forward(self, packet: RecvRemotePacket):
        # 首先辨别接收者addr是谁
        addr = packet.to_addr

        if addr == 'connecting server': # hello包
            await self.server.server_send(packet)

        elif addr in self.functions: # 如果目标就在本机
            # 取出on_recv_func直接打印
            self.functions.get(addr)[0](packet.data)

        else: # 如果目标不在本机，addr仍是虚拟地址
            print("line 230")
            if self.server.has_link(addr): 
                # server发 client接
                await self.server.server_send(packet)

            elif self.client.has_link(addr):
                # client发 server接
                await self.client.client_send(packet)

            else:
                # 如果都发不出去，异常处理
                Reporter.error_addr()
            
class SimulateLogger:
    def __init__(self, name) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(None, f'{cs.server.addr_prefix}/logger-{name}')
        self.name = name

    async def print(self, data: str):
        cs: CSManager = CSManager.get_instance()
        await self.sender.send(f'from {self.name} to printer: {data}', f'{cs.client.addr_prefix}/printer') 

class SimulateExecuter:
    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(self.on_recv, f'{cs.server.addr_prefix}/executer')

    def on_recv(self, config):
        self.run(config)

    def run(self, config):
        print(config)

class SimulatePrinter:
    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        cs.register(self.on_recv, f'{cs.client.addr_prefix}/printer')

    def on_recv(self, data):
        print(f'on_recv: {data}')

class RunBotton:
    sender: ModuleSender

    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(self.run, f'{cs.client.addr_prefix}/run-button')

    async def run(self, config):
        cs: CSManager = CSManager.get_instance()
        await self.sender.send(config, f'{cs.server.addr_prefix}/executer')


if __name__ == '__main__':

    whoami = sys.argv[1]
    # whoami = 'server'

    if whoami == 'server':
        print('I am server')
        cs: CSManager = CSManager.get_instance(host='127.0.0.1', port='9876', addr_prefix='0')

        # launch server
        # cs.server._server_thread_worker()
        thread = threading.Thread(target=cs.server._server_thread_worker)
        thread.start()
        time.sleep(1)

        logger1 = SimulateLogger('logger1')
        logger2 = SimulateLogger('logger2')

        executer = SimulateExecuter()
        printer = SimulatePrinter()

        async def main():
            await logger1.print('111')
            await logger2.print('222')

        step = None
        while step != 'q':
            step = input("< 下一步操作：")
            if step == 'print':
                asyncio.run(main())
        
        

    if whoami == 'client':
        print('I am client')
        cs: CSManager = CSManager.get_instance(host='127.0.0.1', port='9876', addr_prefix='0')  # 这里写的参数是cs实例中任何变量共享的，cs.client和cs.server共享这些变量

        async def main():
            # ip_list = ['ws://127.0.0.1:9876','ws://127.0.0.1:8765']
            ip_list = ['ws://127.0.0.1:9876']

            new_loop = asyncio.get_event_loop() 
            asyncio.run_coroutine_threadsafe(cs.connect(ip_list),new_loop)
            await asyncio.sleep(1)

            button = RunBotton()

            step = None
            while step != 'q':
                step = input("< 下一步操作：")

                if step == 'button':
                    await button.run("< Successful ending.")

            
        asyncio.run(main())