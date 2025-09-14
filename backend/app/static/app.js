let page=1, size=5;
async function fetchStore(q, sort){
  const h={}; const t=localStorage.getItem('token'); if(t) h['Authorization']='Bearer '+t;
  const r=await fetch(/store/search?q=&page=&size=&sort=,{headers:h});
  if(!r.ok) throw new Error('store/search '+r.status);
  return r.json();
}
async function render(){
  const q = document.getElementById('q').value;
  const sort = document.getElementById('sort').value;
  const data = await fetchStore(q, sort);
  const root = document.getElementById('list'); root.innerHTML='';
  (data.items||[]).forEach(it=>{
    const li=document.createElement('li');
    li.textContent = ${it.name} —  — safety: — }{it.usage_cost ?? '-'};
    root.appendChild(li);
  });
  document.getElementById('meta').textContent = Total:  | Sort: ;
  const pageinfo = document.getElementById('pageinfo');
  const lastPage = data.total ? Math.max(1, Math.ceil(data.total/size)) : page;
  pageinfo.textContent = Page  of ;
  document.getElementById('prev').disabled = (page<=1);
  document.getElementById('next').disabled = (page>=lastPage);
}
document.getElementById('s').onclick=()=>{ page=1; render(); };
document.getElementById('sort').onchange=()=>{ page=1; render(); };
document.getElementById('prev').onclick=()=>{ if(page>1){ page--; render(); } };
document.getElementById('next').onclick=()=>{ page++; render(); };
render();
