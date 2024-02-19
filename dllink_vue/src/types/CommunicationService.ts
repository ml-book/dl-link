import { RunButton} from './Register'
import { OpenEvent, DataMessageEvent, CloseEvent, ErrorEvent, ParamMessageEvent, ConnectMessageRecvEvent, ConnectMessageSendEvent} from './KeyEvent'

// namespace
export namespace CommunicationService {
  export let connectUrl: string
  export let connectPort: number
  export let showConnectInfoWindow: boolean
  export function Connect(): void{
    connect()
  }
  export function Button(): void{
    clickButton()
  }
}

let openEvent = OpenEvent.get_instance()
let dataMessageEvent = DataMessageEvent.get_instance()
let closeEvent = CloseEvent.get_instance()
let errorEvent = ErrorEvent.get_instance()
let paramMessageEvent = ParamMessageEvent.get_instance()
let connectMessageRecvEvent = ConnectMessageRecvEvent.get_instance()
let connectMessageSendEvent = ConnectMessageSendEvent.get_instance()

let button = new RunButton()

let execute_config: string | null

let connectUrl = '127.0.0.1'
let connectPort = '9876'
let ws: WebSocket

const connect = () => {
  ws = new WebSocket('ws://' + connectUrl + ':' + connectPort)
  
  ws.onopen = () => {
    openEvent.event(ws)
    connectMessageSendEvent.event(ws)// packet.type === 'connection'
  } 

  ws.onmessage = (evt) => {
    connectMessageRecvEvent.event(ws, evt)// received_msg.type === 'connection'
    execute_config = paramMessageEvent.event(ws, evt)// received_msg.type === 'param'
    dataMessageEvent.event(ws, evt)// received_msg.type === 'string'
  }

  ws.onclose = () => {
    closeEvent.event()
  }

  ws.onerror = () => {
    errorEvent.event()
  }
}

const clickButton = () => {
  if (execute_config === null){
    console.error('"execute_config" is null')
  }
  else{
    button.run(execute_config, "server0/executer")
  }
}

connect() // 确保无论在何时重新加载网页都可以主动尝试连接