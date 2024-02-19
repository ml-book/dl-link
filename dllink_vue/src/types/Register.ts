

interface RecvRemotePacket{
    from_addr: string
    to_addr: string
    type: string
    data: string
}

export function getdefault(map: Map<any, any>, key: any|string){
    if (map.has(key)){
      return map.get(key)
    }
    else { 
      console.error(key + " does not exist as key")
    }
}

export class MyClient{
    static _instance: MyClient
    addr_prefix: string
    links: Map<string, any>
    route_table: Map<string, string>
  
    static get_instance(){
      if (MyClient._instance != null){
        return MyClient._instance
      }
      else {
        MyClient._instance = new MyClient()
        return MyClient._instance
      }
    }
  
    constructor(){
      this.links = new Map();
      this.route_table = new Map()
      this.addr_prefix = 'client0'
    }
  }
  
export class ModuleSender{
  module_addr: string
  manager: any

  constructor(manager:any, module_addr: string) {
    this.manager = manager
    this.module_addr = module_addr
  }

  async send(data: string, addr:string){
    // 构造RecvRemotePacket
    var packet: RecvRemotePacket = {
      from_addr: this.module_addr,
      to_addr: addr,
      type: 'string',
      data: data
    }

    await this.manager.forward(packet)
  }

}
  
export class CSManager{ //注册模块、维护两个字典、把属于客户端的模块都注册到这一边、判断消息的目标地址是server还是client，如果是client则不用转发，如果是server则转发到后端
  functions: Map<string, [any, any]>
  static _instance: CSManager
  client: MyClient
  
  static get_instance(){
    if (CSManager._instance != null){
      return CSManager._instance
    }
    else {
      CSManager._instance = new CSManager()
      return CSManager._instance
    }
  }

  constructor() {
    this.client = MyClient.get_instance()!
    this.functions = new Map();
  }

  register(on_recv_func: Function, addr: string) {
    var sender = new ModuleSender(this, addr)
    this.functions.set(addr, [on_recv_func, sender])
    return sender
  }

  async forward(packet: RecvRemotePacket): Promise<void> {
    const addr = packet.to_addr;
    var to_ip, socket;
    
    // 如果目标在本机
    if (this.functions.has(addr)) {
      const on_recv = getdefault(this.functions, addr)![0]
      on_recv(packet.data)
    } 

    // 如果目标不在本机，发给后端server
    else if (this.client.route_table.has(packet.to_addr.split("/")[0]) || this.client.route_table.has(packet.to_addr)) {

      to_ip = getdefault(this.client.route_table, packet.to_addr.split("/")[0])
      socket = getdefault(this.client.links, to_ip)

      socket.send(JSON.stringify(packet))

    }
    else {
      console.log("没有目标")
    }
  }
}
  
export class RunButton {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.run, cs.client.addr_prefix+"/run-button")
  }

  async run(config: string, to_addr: string): Promise<void>{
    // console.log("line 276: " + this.sender)//this.sender 是undefined
    await this.sender.send(config, to_addr)// "server0/executer"
  }
}
  
export class RecvServer {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.on_recv, cs.client.addr_prefix+"/recv-server")
  }

  on_recv(config: string){
    console.log("server发来的消息是: " + config)
  }
}
  
export class Printer {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.on_recv, cs.client.addr_prefix+"/printer")
  }

  on_recv(config: string){
    console.log("执行日志: " + config)
  }
}

