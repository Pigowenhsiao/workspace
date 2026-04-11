// 容納一鍵更新的核心邏輯框架
async function initUpdatePack(payload){
  // 準備更新包，實作時寫入 skeleton 與草案
  return {ok:true, data:{pack:'prepared'}}
}
async function applyUpdate(payload){
  // 將更新寫入工作區，更新 index.md / AGENTS.md 等
  return {ok:true, data:{applied:true}}
}
async function testUpdate(payload){
  // 產出測試指令與結果
  return {ok:true, data:{tests:['md summary','link check']}}
}

async function handleCall(action,payload){
  switch(action){
    case 'initUpdatePack': return await initUpdatePack(payload)
    case 'applyUpdate': return await applyUpdate(payload)
    case 'testUpdate': return await testUpdate(payload)
    default: return {ok:false, error:'Unknown action'}
  }
}

module.exports = { handleCall }
