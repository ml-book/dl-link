// import {cs, button} from './Register'

// export const connect = () => {
//   cs.ws.onopen = () => {
//     for(let event of cs.events.eventsList.get('onopenevents').function.values()){
//       event(cs.ws)
//     }
//   } 

//   cs.ws.onmessage = (evt) => {
//     for(let event of cs.events.eventsList.get('onmessageevents').function.values()){
//       event(cs.ws, evt)
//     }
//   }

//   cs.ws.onclose = () => {
//     for(let event of cs.events.eventsList.get('oncloseevents').function.values()){
//       event(cs.ws)
//     }
//   }

//   cs.ws.onerror = () => {
//     for(let event of cs.events.eventsList.get('onerrorevents').function.values()){
//       event(cs.ws)
//     }
//   }
// }

// export const clickButton = () => {
//   // 实际上应该传递前端选择的param_config。这里为了方便直接用后端传过来的param_config。
//   if (cs.param_config === null){
//     console.error('"execute_config" is null')
//   }
//   else{
//     button.run(cs.param_config, "server0/executer")
//   }
// }