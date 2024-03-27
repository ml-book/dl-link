"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/10/23 - 11:02
 """
from tests.Decorator import DatasetDict, SplitDict, ModelDict, JudgeDict
from tests.Rewrite_main import NodeManager, execute_all_nodes
from typing import Any, Dict
import websockets
import threading
import asyncio
import time
import json
from dataclasses import dataclass

from typing import Any, Dict
import websockets
import threading
import asyncio
import time
import json
from dataclasses import dataclass

class Reporter:
    @classmethod
    def error_addr(cls):
        print("< 没有目标地址")

@dataclass
class RecvRemotePacket:
    from_addr: str
    to_addr: str
    type: str
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
            type = 'string',
            data = data
        )

        # logger.print()后进入这里，addr是虚拟地址
        await self.manager.forward(packet)

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
                    packet.from_addr, # virtual address
                    (remote_ip, str(remote_port))# corresponding ip
                )

                # router_chain
                await self.router_chain(packet)

            # unset link info
            self.links.pop((remote_ip, str(remote_port)))
            self.route_table.pop(packet.from_addr)

        event_loop.run_until_complete(websockets.serve(onRecv, self.host, self.port))
        event_loop.run_forever()

    async def router_chain(self, packet: RecvRemotePacket):
        cs: CSManager = CSManager.get_instance()
        if packet.type == 'connection':
            await self.server_send(packet)
        else:
            await cs.forward(packet)

    def has_link(self, addr):
        if addr.split("/")[0] in self.route_table or addr in self.route_table:
            return True
        else:
            return False

    async def server_send(self, packet: RecvRemotePacket):
        cs: CSManager = CSManager.get_instance()
        if packet.type == 'connection':
            packet = RecvRemotePacket(
                from_addr = self.addr_prefix,
                to_addr = packet.from_addr,
                type = 'connection',
                data = 'Hi!'
            )
            addr = packet.to_addr
            to_ip = self.route_table.get(addr)# 前端每刷新一次这里的route_table原来存的不会变，是因为键存在就不会再更改值
            socket = self.links.get(to_ip, None)# links会变,links变是正常的。解决方法：196 pop了route_table
            await socket.send(str(packet.__dict__))

        else:
            addr = packet.to_addr
            to_ip = self.route_table.get(addr.split("/")[0])
            socket = self.links.get(to_ip, None)
            await socket.send(str(packet.__dict__))

    def _generate_address_prefix(self) -> str:
        return '0'

class CSManager:
    _instance: Any = None

    def __init__(self, *args, **kwargs) -> None:
        self.server = MyServer.get_instance(*args, **kwargs)
        self.routetable = {}
        self.functions = {}

    @classmethod
    def get_instance(cls, *args, **kwargs):
        assert cls._instance is None or (len(args) == 0 and len(kwargs) == 0)
        if cls._instance is None:
            cls._instance = CSManager(*args, **kwargs)
        return cls._instance

    def register(self, on_recv_func, addr) -> ModuleSender:
        sender = ModuleSender(self, addr)
        self.functions.setdefault(addr, (on_recv_func, sender))
        return sender

    async def forward(self, packet: RecvRemotePacket):
        # 首先辨别接收者addr是谁
        addr = packet.to_addr

        if addr in self.functions: # 如果目标就在本机
            # 取出on_recv_func直接打印
            self.functions.get(addr)[0](packet.data)

        else: # 如果目标不在本机，addr仍是虚拟地址
            if self.server.has_link(addr): # to_addr如果是client下面的地址，那么这一条是能够通过的
                # server发 client接
                await self.server.server_send(packet)

            else:
                # 如果都发不出去，异常处理
                Reporter.error_addr()

class SimulateLogger:
    sender: ModuleSender

    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(None, f'{cs.server.addr_prefix}/logger')

    async def print(self, data: str):
        cs: CSManager = CSManager.get_instance()
        await self.sender.send(f'from {self.name} to printer: {data}', 'client0/printer')

class SimulateExecuter:
    sender: ModuleSender

    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(self.on_recv, f'{cs.server.addr_prefix}/executer')

    def on_recv(self, config):
        print(config)

class Send_to_client:
    sender: ModuleSender

    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(self.run, f'{cs.server.addr_prefix}/send-client')

    async def run(self, config):
        cs: CSManager = CSManager.get_instance()
        await self.sender.send(config, 'client0/recv-server')


if __name__ == '__main__':
    manager = NodeManager(if_parallel=False)
    send_params = manager.get_all_params()
    DatasetDict(manager)
    SplitDict(manager)
    ModelDict(manager)
    JudgeDict(manager)
    dataset = manager.registed_nodes["dataset"]
    spliter = manager.registed_nodes["data_split"]
    model = manager.registed_nodes["model"]
    judger = manager.registed_nodes["judger"]

    split_result = spliter.split(dataset)
    X_train, X_test, y_train, y_test = (split_result[i] for i in range(4))
    model.fit(X_train, y_train)
    # temp = model.train(X_train, y_train)
    # temp > predict 实现temp优先于predict计算
    y_predict = model.predict(X_test)
    judger.judge(y_test, y_predict)


    print('I am server')
    cs: CSManager = CSManager.get_instance(host='127.0.0.1', port='9876', addr_prefix='0')

    thread = threading.Thread(target=cs.server._server_thread_worker)
    thread.start()
    time.sleep(1)

    logger = SimulateLogger()

    executer = SimulateExecuter()

    send_to_client = Send_to_client()

    async def main():
        await send_to_client.run(send_params.__str__())

    while(input()):
        asyncio.run(main())

    execute_all_nodes(manager, {
        'dataset': 'iris',
        'data_split': 'ratio:0.8',
        'model': {
            'name': 'svm',
            'params': {
                'kernel': 'default'
            }
        },
        'judger': 'judge_clf'
    })
    print(0)





