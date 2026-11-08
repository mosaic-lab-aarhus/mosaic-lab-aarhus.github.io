document.body.classList.add("has-js");
const toggle=document.querySelector(".menu-toggle");
const nav=document.querySelector("#site-nav");
if(toggle&&nav){toggle.hidden=false;toggle.addEventListener("click",()=>{const open=toggle.getAttribute("aria-expanded")==="true";toggle.setAttribute("aria-expanded",String(!open));nav.dataset.open=String(!open);toggle.textContent=open?"Menu":"Close";});document.addEventListener("keydown",event=>{if(event.key==="Escape"&&nav.dataset.open==="true"){nav.dataset.open="false";toggle.setAttribute("aria-expanded","false");toggle.textContent="Menu";toggle.focus();}});}
const filters=document.querySelectorAll("[data-year-filter]");
const pubGroups=document.querySelectorAll("[data-publication-year]");
if(filters.length){document.querySelector(".filter-bar").hidden=false;for(const button of filters){button.addEventListener("click",()=>{const year=button.dataset.yearFilter;for(const peer of filters)peer.setAttribute("aria-pressed",String(peer===button));let count=0;for(const group of pubGroups){group.hidden=year!=="all"&&group.dataset.publicationYear!==year;if(!group.hidden)count+=group.querySelectorAll(".publication").length;}document.querySelector("#publication-count").textContent=count+" publication"+(count===1?"":"s")+" shown";});}}
