
import ast
import sys
sys.path.append(r"D:\Aa-AAA机器学习实践教材\‏dllink\dlframe_back_master")
from tests.Decorator import DatasetDict, SplitDict, ModelDict, JudgeDict
from tests.Rewrite_main import NodeManager, execute_all_nodes
from asyncio.coroutines import iscoroutine

from typing import Any, Dict
import websockets
import threading
import asyncio
import time
import json
from dataclasses import dataclass
import io
import datetime


#改变标准输出的默认编码
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

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
        self.module_addr = module_addr # module virtual address

    async def send(self, data: str, addr: str):
        # packet contruction
        packet = RecvRemotePacket(
            from_addr = self.module_addr,
            to_addr = addr,
            type = "string",
            data = data
        )

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

            # # unset link info
            # self.links.pop((remote_ip, str(remote_port)))
            # self.route_table.pop(packet.from_addr)

            # unset link info 3.26
            self.links = {}
            self.route_table = {}
            # self.links.pop((remote_ip, str(remote_port)))
            # self.route_table.pop(packet.from_addr)

        event_loop.run_until_complete(websockets.serve(onRecv, self.host, self.port))
        event_loop.run_forever()

    async def router_chain(self, packet: RecvRemotePacket):
        cs: CSManager = CSManager.get_instance()
        if packet.type == 'connection':
            await self.server_send(packet)
        elif packet.type == 'pre-param':
            await self.server_send(packet)
        else:
            await cs.forward(packet)

    def has_link(self, addr):
        if addr.split("/")[0] in self.route_table or addr in self.route_table:
            return True
        else:
            return False

    async def server_send(self, packet: RecvRemotePacket):
        # Hello packet 
        if packet.type == 'connection':
            packet = RecvRemotePacket(
                from_addr = self.addr_prefix,
                to_addr = packet.from_addr,
                type = "connection",
                data = "Hi!"
            )
            addr = packet.to_addr
            to_ip = self.route_table.get(addr) # virtual address -> corresponding ip
            socket = self.links.get(to_ip, None) # corresponding ip -> socket
            await socket.send(str(packet.__dict__))
        
        # params packet
        elif packet.type == 'pre-param':
            packet = RecvRemotePacket(
                from_addr = self.addr_prefix,
                to_addr = packet.from_addr,
                type = "param",
                data = selected_params_dict # 这里换成 -> send_params，不用.__str__()
            )
            addr = packet.to_addr
            to_ip = self.route_table.get(addr) # virtual address -> corresponding ip
            socket = self.links.get(to_ip, None) # corresponding ip -> socket
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
        self.server: MyServer = MyServer.get_instance(*args, **kwargs)
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
        addr = packet.to_addr

        if addr in self.functions: # if destination in local server
            if not iscoroutine(self.functions.get(addr)[0]): # 不是协程，不可await
                self.functions.get(addr)[0](packet.data)
            else: # 是协程，可await 
                await self.functions.get(addr)[0](packet.data)

        else: # if destination in local client
            if self.server.has_link(addr):
                await self.server.server_send(packet)

            else:
                # no destination address
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

    def __init__(self, manager) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(self.on_recv, f'{cs.server.addr_prefix}/executer')
        self.manager = manager

    def on_recv(self, config):
        execute_all_nodes(self.manager, config)

class Send_to_client:
    sender: ModuleSender

    def __init__(self) -> None:
        cs: CSManager = CSManager.get_instance()
        self.sender = cs.register(self.run, f'{cs.server.addr_prefix}/send-client')

    async def run(self, config):
        cs: CSManager = CSManager.get_instance()
        await self.sender.send(config, 'client0/recv-server')


if __name__ == '__main__':

    # 注册所需的参数节点 如0.8 然后在 spliter = manager.registed_nodes["data_split"] 时传入0.8的节点

    manager = NodeManager(if_parallel=False)
    params = manager.get_all_params()

    # 发给前端
    print(str(params))

    DatasetDict(manager)
    SplitDict(manager)
    ModelDict(manager)
    JudgeDict(manager)
    dataset = manager.registed_nodes["dataset"]
    spliter = manager.registed_nodes["data_split"]

    # manager.register("ratio", {"0.8": 0.8, "0.5": 0.5})     # 未实现,create_node方法
    # Spliter = manager.registed_nodes["data_split"]
    # ratio = manager.registed_nodes["ratio"]
    # spliter = Spliter(ratio)

    model = manager.registed_nodes["model"]
    judger = manager.registed_nodes["judger"]

    split_result = spliter.split(dataset)
    X_train, X_test, y_train, y_test = (split_result[i] for i in range(4))
    model.fit(X_train, y_train)
    # temp = model.train(X_train, y_train)
    # temp > predict 实现temp优先于predict计算
    y_predict = model.predict(X_test)
    judger.judge(y_test, y_predict)

    # 从前端获取已选择的参数（str
    test_str = "{'dataset': 'iris', 'data_split': 'ratio:0.8', 'model': {'name': 'svm', 'params': {'kernel': 'default'}}, 'judger': 'judge_clf'}"
    selected_params_dict = ast.literal_eval(test_str)   # 字符串转换为字典
    # test_str = {'model': {'option': 'SVM','args': {'kernel': 'default'}},'dataset': {'option': 'Iris','args': {}},'data_split': {'option': 'TestSplitter','args': {'ratio': 0.8}},'judger': {'option': 'Judger_Rlf','args': {}}}

    # ===========================================================================
    # launch a server
    print('I am server')
    cs: CSManager = CSManager.get_instance(host='127.0.0.1', port='9876', addr_prefix='0')
    thread = threading.Thread(target=cs.server._server_thread_worker)
    thread.start()
    time.sleep(1)

    # register modules
    logger = SimulateLogger()
    executer = SimulateExecuter(manager)


    # ===========================================================================

    # execute_all_nodes(manager, selected_params_dict)    # 最终执行
    # print(0)


