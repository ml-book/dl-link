import { ElMessage } from 'element-plus'
import { MyClient, CSManager, getdefault} from './Register'

let client:MyClient = MyClient.get_instance()
let cs:CSManager = CSManager.get_instance()

let param_config: string = ''

let connectUrl = '127.0.0.1'
let connectPort = '9876'
let isConnectedToServer = false
export let showConnectInfoWindow = false

export class OpenEvent{
    static _instance: OpenEvent
  
    static get_instance(){
      if (OpenEvent._instance != null){
        return OpenEvent._instance
      }
      else {
        OpenEvent._instance = new OpenEvent()
        return OpenEvent._instance
      }
    }
  
    constructor(){}

    event(ws: WebSocket){
        isConnectedToServer = true
        showConnectInfoWindow = false
        ElMessage({
            message: '连接成功',
            type: 'success',
        })
    
        // setup link info
        client.links.set(
            connectUrl + ':' + connectPort,
            ws
        )
    }
}

export class DataMessageEvent{
    static _instance: DataMessageEvent
  
    static get_instance(){
      if (DataMessageEvent._instance != null){
        return DataMessageEvent._instance
      }
      else {
        DataMessageEvent._instance = new DataMessageEvent()
        return DataMessageEvent._instance
      }
    }
  
    constructor(){}

    event(ws: WebSocket, evt: any){
        // json的格式必须是内部双引号
        // console.log(evt.data.replaceAll("'", '"'))
        let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
        // console.log(received_msg)
        
        if (ws.CONNECTING === 0) {
            const received_msg_data = received_msg.data
    
            if (received_msg.type === 'string') {
                cs.forward(received_msg)
            }
    
            else if (received_msg.type === 'has_link'){ // 目前没用
                let to_ip, socket
                const received_msg_addr = received_msg.to_addr
    
                if (client.route_table.has(received_msg_addr.spilt("/")[0]) || client.route_table.has(received_msg_addr)){
                    to_ip = getdefault(client.route_table, received_msg_data("/")[0])
                    socket = getdefault(client.links, to_ip)
                    socket.send(evt.data)
                }
                else {
                    console.log("没有目标地址")
                }
            }
        } 
    
        else {
            console.error(received_msg.data);
        }
    }
    
}

export class CloseEvent{
    static _instance: CloseEvent
  
    static get_instance(){
      if (CloseEvent._instance != null){
        return CloseEvent._instance
      }
      else {
        CloseEvent._instance = new CloseEvent()
        return CloseEvent._instance
      }
    }
  
    constructor(){}

    event(){
        isConnectedToServer = false
        showConnectInfoWindow = true
        ElMessage.error('连接已断开')
    }
}

export class ErrorEvent{
    static _instance: ErrorEvent
  
    static get_instance(){
      if (ErrorEvent._instance != null){
        return ErrorEvent._instance
      }
      else {
        ErrorEvent._instance = new ErrorEvent()
        return ErrorEvent._instance
      }
    }
  
    constructor(){}

    event(){
        ElMessage.error('连接失败(地址错误 / 协议错误 / 服务器错误)')
        showConnectInfoWindow = true
    }
}

export class ParamMessageEvent{
    static _instance: ParamMessageEvent
  
    static get_instance(){
      if (ParamMessageEvent._instance != null){
        return ParamMessageEvent._instance
      }
      else {
        ParamMessageEvent._instance = new ParamMessageEvent()
        return ParamMessageEvent._instance
      }
    }
  
    constructor(){}

    event(ws: WebSocket, evt: any){
        let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
        if (ws.CONNECTING === 0){
            if (received_msg.type === 'param'){
                // 接收后端传过来的参数
                console.log(received_msg.data)
                param_config = received_msg.data
                return param_config
            }
            else{
                return null
            }
        }
        else {
            console.error(received_msg.data);
            return null
        }
    }
}

export class ConnectMessageRecvEvent{
    static _instance: ConnectMessageRecvEvent
  
    static get_instance(){
      if (ConnectMessageRecvEvent._instance != null){
        return ConnectMessageRecvEvent._instance
      }
      else {
        ConnectMessageRecvEvent._instance = new ConnectMessageRecvEvent()
        return ConnectMessageRecvEvent._instance
      }
    }
  
    constructor(){}

    event(ws: WebSocket, evt: any){
        let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
        if (ws.CONNECTING === 0){
            // 整个连接过程中只有两个方向完全相反的connection包，它传递后端虚拟地址
            if (received_msg.type === 'connection') {
                // setup link info
                client.route_table.set(
                    received_msg.from_addr,
                    connectUrl + ':' + connectPort
                )

                // 收到之后在返回ack，让服务器发参数
                ws.send(JSON.stringify({
                    from_addr: 'client0', // 这里先直接填入，应该考虑起名的问题
                    to_addr: '',
                    type: 'pre-param',
                    data: 'ACK'
                }))
    
            }
        }
        else {
            console.error(received_msg.data);
        }
    }
}

export class ConnectMessageSendEvent{
    static _instance: ConnectMessageSendEvent
  
    static get_instance(){
      if (ConnectMessageSendEvent._instance != null){
        return ConnectMessageSendEvent._instance
      }
      else {
        ConnectMessageSendEvent._instance = new ConnectMessageSendEvent()
        return ConnectMessageSendEvent._instance
      }
    }
  
    constructor(){}

    event(ws: WebSocket){
        // 这个包即是hello包，又是 确认已连接 包
        ws.send(JSON.stringify({
            from_addr: 'client0', // 这里先直接填入，应该考虑起名的问题
            to_addr: '',
            type: 'connection',
            data: 'Hello!'
        }))
    }
}