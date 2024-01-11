(()=>{"use strict";function t(t,e){const o=Math.min(...t),n=Math.max(...t);let a="hour";return n-o>864e5*e&&(a="day"),n-o>2592e6*e&&(a="month"),n-o>7776e6*e&&(a="quarter"),n-o>31536e6*e&&(a="year"),a}function e(t){return t.split(" ").filter((t=>/\p{L}/giu.test(t)))}function o(t,e){const o=t.head.cells.findIndex((t=>t.text===e));if(o<0)throw new Error("column ".concat(t.id,".").concat(e," not found"));return t.body.rows.map((t=>t.cells[o].text))}function n(t,e,o,n,a){return(t-e)/(o-e)*(a-n)+n}async function a(e,n){const a={type:n.type,xKey:{label:void 0!==n.group.label?n.group.label:n.group.column},yKeys:{},data:[]};if(0===e.body.rows.length)return a;const r=e.body.rows.map((t=>t.id));let l=o(e,n.group.column);if(0===l.length)throw new Error("X column ".concat(e.id,".").concat(n.group.column," not found"));let u=null;void 0!==n.group.dateFormat&&([l,u]=function(e,o){let n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:10,a=e;const r=e.map((t=>new Date(t).getTime()));let l=null;if("auto"===o&&(o=t(r,n)),"year"===o&&(a=r.map((t=>new Date(t).getFullYear().toString())),l=r),"quarter"===o&&(a=r.map((t=>{const e=new Date(t).getFullYear().toString(),o=Math.floor(new Date(t).getMonth()/3)+1;return"".concat(e,"-Q").concat(o)})),l=r),"month"===o&&(a=r.map((t=>new Date(t).getFullYear().toString()+"-"+new Date(t).toLocaleString("default",{month:"short"}))),l=r),"day"===o&&(a=r.map((t=>new Date(t).toISOString().split("T")[0])),l=r),"hour"===o&&(a=r.map((t=>new Date(t).toISOString().split("T")[1].split(":")[0])),l=r),"month_cycle"===o){const t=new Intl.DateTimeFormat("default",{month:"long"});a=r.map((e=>t.format(new Date(e)))),l=r.map((t=>new Date(t).getMonth()))}if("weekday_cycle"===o){const t=new Intl.DateTimeFormat("default",{weekday:"long"});a=r.map((e=>t.format(new Date(e)))),l=r.map((t=>new Date(t).getDay()))}if("day_cycle"===o){const t=new Intl.DateTimeFormat("default",{day:"numeric"});a=r.map((e=>t.format(new Date(e)))),l=r.map((t=>new Date(t).getDay()))}if("hour_cycle"===o){const t=new Intl.DateTimeFormat("default",{hour:"numeric"});a=r.map((e=>t.format(new Date(e)))),l=r.map((t=>new Date(t).getHours()))}return[a,l]}(l,n.group.dateFormat));const s={};for(const t of n.values){var c;const n=void 0!==t.aggregate?t.aggregate:"count";let d="default";"pct"!==n&&"count_pct"!==n||(d="percent");const p=o(e,t.column);if(0===p.length)throw new Error("Y column ".concat(e.id,".").concat(t.column," not found"));const v=void 0!==t.group_by?o(e,t.group_by):null,f=null!==(c=t.addZeroes)&&void 0!==c&&c,y={},g=new Set([]);for(let e=0;e<l.length;e++){var i;const o=l[e],c=p[e],w=null!=v?v[e]:void 0!==t.label?t.label:t.column;f&&g.add(w);const h=null!=u?u[e]:l[e];var m;if(void 0===y[w]&&(y[w]={n:0,sum:0}),"count_pct"!==n&&"mean"!==n||(y[w].n+=1),"pct"===n&&(y[w].sum+=null!==(i=Number(c))&&void 0!==i?i:0),void 0===a.yKeys[w]&&(a.yKeys[w]={label:w,secondAxis:void 0!==t.secondAxis,tickerFormat:d}),void 0===s[o]&&(s[o]={sortBy:h,rowIds:{},xLabel:a.xKey.label,xValue:String(o),values:{}}),void 0===s[o].rowIds[w]&&(s[o].rowIds[w]=[]),s[o].rowIds[w].push(r[e]),void 0===s[o].values[w]&&(s[o].values[w]=0),"count"!==n&&"count_pct"!==n||(s[o].values[w]+=1),"sum"===n||"mean"===n||"pct"===n)s[o].values[w]+=null!==(m=Number(c))&&void 0!==m?m:0}Object.keys(y).forEach((t=>{for(const e of Object.keys(s)){if(void 0===s[e].values[t]){if(!f)continue;s[e].values[t]=0}"mean"===n&&(s[e].values[t]=Number(s[e].values[t])/y[t].n),"count_pct"===n&&(s[e].values[t]=100*Number(s[e].values[t])/y[t].n),"pct"===n&&(s[e].values[t]=100*Number(s[e].values[t])/y[t].sum)}}))}return a.data=Object.values(s).sort(((t,e)=>t.sortBy<e.sortBy?-1:e.sortBy<t.sortBy?1:0)).map((t=>{for(const e of Object.keys(t.values))t.values[e]=Math.round(100*t.values[e])/100;return{...t.values,[t.xLabel]:t.xValue,__rowIds:t.rowIds,__sortBy:t.sortBy}})),a}async function r(t,a){const r={type:a.type,topTerms:[]};if(0===t.body.rows.length)return r;const l=o(t,a.textColumn),u=function(t,o,n){const a={};for(let l=0;l<t.length;l++){if(null==(null===t||void 0===t?void 0:t[l]))continue;const u=t[l],s=null!=n.tokenize&&n.tokenize?e(u):[u],c=new Set;for(const t of s){var r;void 0===a[t]&&(a[t]={value:0,docFreq:0}),c.has(t)||(a[t].docFreq+=1,c.add(t));const e=null!==(r=Number(null===o||void 0===o?void 0:o[l]))&&void 0!==r?r:1;isNaN(e)||(a[t].value+=e)}}return a}(l,null!=a.valueColumn?o(t,a.valueColumn):null,a);return r.topTerms=function(t,e,o){const a=Object.entries(t).map((t=>{let[o,n]=t;const a=Math.log(1+n.value),r=Math.log(e/n.docFreq);return{text:o,value:n.value,importance:a*r}})).sort(((t,e)=>e.importance-t.importance)).slice(0,o),r=Math.min(...a.map((t=>t.importance))),l=Math.max(...a.map((t=>t.importance)));return a.map((t=>({text:t.text,value:t.value,importance:n(t.importance,r,l,0,1)})))}(u,l.length,200),r}self.onmessage=t=>{(async function(t,e){if(void 0===t||void 0===e)throw new Error("Table and visualization are required");if(["line","bar","area"].includes(e.type))return await a(t,e);if(["wordcloud"].includes(e.type))return await r(t,e);throw new Error("Visualization type ".concat(e.type," not supported"))})(t.data.table,t.data.visualization).then((t=>{self.postMessage({status:"success",visualizationData:t})})).catch((t=>{console.error(t),self.postMessage({status:"error",visualizationData:void 0})}))}})();
//# sourceMappingURL=448.21dda5a7.chunk.js.map