async function pingInfo(){
  try{
    const r = await fetch("/info");
    const j = await r.json();
    alert("Info: " + JSON.stringify(j));
  }catch(e){
    alert("Failed: " + e);
  }
}
document.addEventListener("DOMContentLoaded", ()=>{
  const btn = document.getElementById("clickme");
  if(btn){ btn.addEventListener("click", pingInfo); }
});
