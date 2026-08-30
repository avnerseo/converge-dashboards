function toggleTheme(){var el=document.documentElement,c=el.getAttribute('data-theme');if(c==='dark'){el.setAttribute('data-theme','light');}else if(c==='light'){el.removeAttribute('data-theme');}else{el.setAttribute('data-theme','dark');}}

function filterAll(){
  var q=document.getElementById('globalSearch').value.trim().toLowerCase();
  document.querySelectorAll('.stock-card[data-q]').forEach(function(c){c.style.display=(!q||c.dataset.q.indexOf(q)!==-1)?'':'none';});
  document.querySelectorAll('.tab-panel.active tbody tr[data-q]').forEach(function(r){r.style.display=(!q||r.dataset.q.indexOf(q)!==-1)?'':'none';});
}

function showTab(tabId){
  document.querySelectorAll('.tab-panel').forEach(function(p){p.classList.remove('active');});
  document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active');});
  document.getElementById('panel-'+tabId).classList.add('active');
  document.querySelector('.tab-btn[data-tab="'+tabId+'"]').classList.add('active');
  filterAll();
}

function sortTable(tableId,colIndex,isNumeric){
  var table=document.getElementById(tableId);
  var tbody=table.tBodies[0];
  var rows=Array.prototype.slice.call(tbody.querySelectorAll('tr'));
  var curCol=table.getAttribute('data-sort-col');
  var curDir=table.getAttribute('data-sort-dir');
  var dir=(curCol==String(colIndex)&&curDir==='asc')?'desc':'asc';
  rows.sort(function(a,b){
    var ca=a.cells[colIndex],cb=b.cells[colIndex];
    var av=ca.getAttribute('data-sort');av=(av!==null)?parseFloat(av):ca.textContent.trim();
    var bv=cb.getAttribute('data-sort');bv=(bv!==null)?parseFloat(bv):cb.textContent.trim();
    if(isNumeric){av=parseFloat(av)||0;bv=parseFloat(bv)||0;return dir==='asc'?av-bv:bv-av;}
    av=String(av);bv=String(bv);
    return dir==='asc'?av.localeCompare(bv,'he'):bv.localeCompare(av,'he');
  });
  rows.forEach(function(r){tbody.appendChild(r);});
  table.setAttribute('data-sort-dir',dir);
  table.setAttribute('data-sort-col',colIndex);
}

function exportVisibleCSV(tableId){
  var table=document.getElementById(tableId);
  var rows=table.querySelectorAll('tr');
  var csv=[];
  rows.forEach(function(r){
    if(r.style.display==='none')return;
    var cells=Array.prototype.slice.call(r.querySelectorAll('th,td'));
    var cols=cells.map(function(c){return '"'+c.textContent.trim().replace(/"/g,'""')+'"';});
    csv.push(cols.join(','));
  });
  var blob=new Blob(["﻿"+csv.join('\n')],{type:'text/csv;charset=utf-8;'});
  var link=document.createElement('a');
  link.href=URL.createObjectURL(blob);
  link.download=tableId+'-converge.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function syncQuicknavHeight(){
  var qn=document.getElementById('quicknav');
  if(!qn)return;
  document.documentElement.style.setProperty('--qn-height',(qn.offsetHeight+14)+'px');
}
window.addEventListener('load',syncQuicknavHeight);
window.addEventListener('resize',syncQuicknavHeight);
if(window.ResizeObserver){
  var qnEl=document.getElementById('quicknav');
  if(qnEl){new ResizeObserver(syncQuicknavHeight).observe(qnEl);}
}
syncQuicknavHeight();
