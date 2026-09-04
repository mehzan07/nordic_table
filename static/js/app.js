const dishes=[
["Starters","Toast Skagen","Hand-peeled prawns, dill, lemon, horseradish and toasted sourdough.","145 kr","https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=700&q=80"],
["Starters","Burrata & Tomatoes","Creamy burrata, tomatoes, basil oil, toasted seeds and sea salt.","139 kr","https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=700&q=80"],
["Starters","Crispy Calamari","Golden calamari, lemon, parsley and smoked garlic aioli.","135 kr","https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=700&q=80"],
["Main","Grilled Salmon","Grilled salmon, crushed potatoes, seasonal greens and lemon butter.","249 kr","https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=700&q=80"],
["Main","Beef Tenderloin","Swedish beef tenderloin, potato gratin, red-wine sauce and roasted vegetables.","329 kr","https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=700&q=80"],
["Main","Herb Chicken","Herb-roasted chicken breast, parmesan potatoes, green beans and natural jus.","219 kr","https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=700&q=80"],
["Pasta","Truffle Mushroom Pasta","Tagliatelle, roasted mushrooms, parmesan, herbs and truffle cream.","219 kr","https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=700&q=80"],
["Pasta","Prawn Linguine","Linguine, prawns, cherry tomatoes, garlic, chili, parsley and lemon.","239 kr","https://images.unsplash.com/photo-1556761223-4c4282c73f77?auto=format&fit=crop&w=700&q=80"],
["Vegetarian","Roasted Cauliflower","Roasted cauliflower, herb lentils, tahini, pomegranate and toasted almonds.","199 kr","https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=700&q=80"],
["Vegetarian","Wild Mushroom Risotto","Creamy risotto, wild mushrooms, aged cheese, herbs and crispy shallots.","209 kr","https://images.unsplash.com/photo-1476124369491-e7addf5db371?auto=format&fit=crop&w=700&q=80"],
["Burgers","Classic House Burger","Swedish beef, cheddar, lettuce, tomato, pickles and house dressing with fries.","199 kr","https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=700&q=80"],
["Desserts","Crème Brûlée","Classic vanilla crème brûlée with caramelized sugar and fresh berries.","109 kr","https://images.unsplash.com/photo-1470324161839-ce2bb6fa6bc3?auto=format&fit=crop&w=700&q=80"],
["Desserts","Chocolate Fondant","Warm chocolate fondant, vanilla ice cream and seasonal berries.","119 kr","https://images.unsplash.com/photo-1606313564200-e75d5e30476b?auto=format&fit=crop&w=700&q=80"],
["Desserts","Tiramisu","Espresso-soaked sponge, mascarpone cream and cocoa.","105 kr","https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=700&q=80"],
["Drinks","Fresh Lemonade","Fresh lemon, mint, sparkling water and a touch of honey.","55 kr","https://images.unsplash.com/photo-1621263764928-df1444c5b8e4?auto=format&fit=crop&w=700&q=80"],
["Drinks","Sparkling Elderflower","Elderflower, lime, mint and sparkling water.","59 kr","https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=700&q=80"]
];
const grid=document.querySelector("#menuGrid"), filters=document.querySelector("#filters"), search=document.querySelector("#menuSearch");
const cats=["All",...new Set(dishes.map(x=>x[0]))];
filters.innerHTML=cats.map(c=>`<button class="${c==="All"?"active":""}" data-cat="${c}">${c}</button>`).join("");
let currentCat="All", currentQuery="";
function render(){
  const q=currentQuery.trim().toLowerCase();
  const list=dishes.filter(d=>{
    const catOk=currentCat==="All"||d[0]===currentCat;
    const sv=(typeof dishSv!=="undefined"&&dishSv[d[1]])||[];
    const haystack=`${d[1]} ${d[2]} ${d[0]} ${sv[0]||""} ${sv[1]||""} ${(typeof categorySv!=="undefined"&&categorySv[d[0]])||""}`.toLowerCase();
    return catOk && (!q || haystack.includes(q));
  });

  const lang=(typeof currentLanguage!=="undefined" ? currentLanguage : "sv");
  const viewText=lang==="sv" ? "Visa detaljer" : "View details";
  const bookText=lang==="sv" ? "Boka bord" : "Book a table";

  grid.innerHTML=list.length ? list.map(d=>{
    const index=dishes.indexOf(d);
    const sv=(typeof dishSv!=="undefined"&&dishSv[d[1]])||null;
    const title=lang==="sv"&&sv?sv[0]:d[1];
    const desc=lang==="sv"&&sv?sv[1]:d[2];
    const cat=lang==="sv"&&typeof categorySv!=="undefined"?(categorySv[d[0]]||d[0]):d[0];
    return `<article class="dish" data-index="${index}" tabindex="0">
      <img src="${d[4]}" alt="${title}" loading="lazy">
      <div class="dishContent">
        <div class="dishMeta"><small>${cat}</small><span class="price">${d[3]}</span></div>
        <h3>${title}</h3>
        <p>${desc}</p>
        <div class="dishActions">
          <button type="button" class="dishDetailsBtn" data-action="details" data-index="${index}">${viewText}</button>
          <button type="button" class="dishBookBtn" data-action="book" data-index="${index}">${bookText}</button>
        </div>
      </div>
    </article>`;
  }).join("") : `<div class="emptyMenu"><h3>${lang==="sv"?"Inga rätter hittades":"No dishes found"}</h3><p>${lang==="sv"?"Prova en annan sökning eller välj Alla.":"Try another search or choose All."}</p></div>`;
}
render();
filters.addEventListener("click",e=>{if(e.target.tagName!=="BUTTON")return;filters.querySelectorAll("button").forEach(b=>b.classList.remove("active"));e.target.classList.add("active");currentCat=e.target.dataset.cat;render()});
search.addEventListener("input",()=>{currentQuery=search.value;render()});

const modal=document.querySelector("#dishModal"),
  modalImage=document.querySelector("#modalImage"),
  modalCategory=document.querySelector("#modalCategory"),
  modalTitle=document.querySelector("#modalTitle"),
  modalDescription=document.querySelector("#modalDescription"),
  modalPrice=document.querySelector("#modalPrice");

let currentDishIndexV29 = null;

function openDish(index){
  currentDishIndexV29 = index;
  const d=dishes[index];
  if(!d)return;
  const sv=(typeof dishSv!=="undefined"&&dishSv[d[1]])||null;
  const lang=(typeof currentLanguage!=="undefined" ? currentLanguage : "sv");
  const title=lang==="sv"&&sv?sv[0]:d[1];
  const desc=lang==="sv"&&sv?sv[1]:d[2];
  const cat=lang==="sv"&&typeof categorySv!=="undefined"?(categorySv[d[0]]||d[0]):d[0];
  modalImage.src=d[4];
  modalImage.alt=title;
  modalCategory.textContent=cat;
  modalTitle.textContent=title;
  modalDescription.textContent=desc;
  modalPrice.textContent=d[3];
  modal.classList.add("show");
  modal.setAttribute("aria-hidden","false");
  document.body.classList.add("modalOpen");
}

function closeDish(){
  modal.classList.remove("show");
  modal.setAttribute("aria-hidden","true");
  document.body.classList.remove("modalOpen");
}

function goToReservation(){
  if(currentDishIndexV29 !== null && dishes[currentDishIndexV29]){
    setSelectedDishV29(dishes[currentDishIndexV29]);
  }
  closeDish();
  const section=document.getElementById("reservation");
  if(section)setTimeout(()=>section.scrollIntoView({behavior:"smooth",block:"start"}),50);
}

grid.addEventListener("click",e=>{
  const button=e.target.closest("button[data-action]");
  if(button){
    e.stopPropagation();
    const index=Number(button.dataset.index);
    if(button.dataset.action==="details") openDish(index);
    if(button.dataset.action==="book"){
      setSelectedDishV29(dishes[index]);
      const section=document.getElementById("reservation");
      if(section)section.scrollIntoView({behavior:"smooth",block:"start"});
    }
    return;
  }
  const card=e.target.closest(".dish");
  if(card)openDish(Number(card.dataset.index));
});

grid.addEventListener("keydown",e=>{
  if((e.key==="Enter"||e.key===" ")&&e.target.classList.contains("dish")){
    e.preventDefault();
    openDish(Number(e.target.dataset.index));
  }
});

document.querySelector("#modalClose").addEventListener("click",closeDish);
document.querySelector("#modalCloseSecondary").addEventListener("click",closeDish);
document.querySelector("#modalReserveNow").addEventListener("click",goToReservation);
modal.addEventListener("click",e=>{if(e.target===modal)closeDish()});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&modal.classList.contains("show"))closeDish()});

const nav=document.querySelector(".nav");const toggle=document.querySelector("#toggle");toggle.onclick=()=>{const open=nav.classList.toggle("open");toggle.setAttribute("aria-expanded",open)};nav.querySelectorAll("nav a").forEach(a=>a.addEventListener("click",()=>{nav.classList.remove("open");toggle.setAttribute("aria-expanded","false")}));

/* Version 5: bilingual Swedish/English + reservation communication improvements */
(function(){
  const form=document.getElementById("reservationForm");
  if(!form)return;
  const dateEl=document.getElementById("reservationDate");
  const review=document.getElementById("reservationReview");
  const details=document.getElementById("reviewDetails");
  const message=document.getElementById("reservationSent");
  const help=document.getElementById("communicationHelp");
  const emailBtn=document.getElementById("sendReservation");
  const smsBtn=document.getElementById("sendSms");
  const editBtn=document.getElementById("editReservation");
  const copyBtn=document.getElementById("copyReservation");
  const mailAddress="reservations@testrestaurant.se";
  let currentLanguage=localStorage.getItem("testRestaurantLanguage")||"sv";
  let reservationData=null;

  const T={
    sv:{"reservation.selectedDish":"Vald rätt","reservation.removeDish":"Ta bort","reservation.noDish":"Ingen vald rätt","menu.view":"Visa detaljer","menu.book":"Boka bord","menu.close":"Stäng","menu.priceLabel":"Pris","menu.servingLabel":"Servering","menu.servingValue":"Tillagas på beställning","menu.allergyLabel":"Allergier","menu.allergyValue":"Fråga gärna personalen",
      "top.open":"Öppet idag 11:00–23:00","top.call":"Ring +46 08 123 45 67","nav.home":"Hem","nav.about":"Om oss","nav.menu":"Meny","nav.reservation":"Boka bord","nav.contact":"Kontakt","nav.book":"Boka ett bord",
      "hero.kicker":"VÄLKOMMEN TILL TEST RESTAURANT","hero.title":"God mat.<br><i>Härliga stunder.</i>","hero.text":"En modern matupplevelse där färska råvaror, varm service och minnesvärda smaker möts.","hero.explore":"Se menyn",
      "about.kicker":"VÅR HISTORIA","about.title":"En plats för <i>trevligt sällskap.</i>","about.p1":"Test Restaurant är ett modernt demokoncept som visar hur en professionell restaurangwebbplats kan se ut och fungera.","about.p2":"Kom för en avslappnad lunch, en speciell middag eller bara en god dessert. Varje detalj är utformad för en trevlig upplevelse.","about.mon":"Måndag <b>Stängt</b>","about.tueThu":"Tis–Tor <b>11:00–22:00</b>","about.fri":"<div class=\"hours-line\"><span>Fre–Lör</span><strong>11:00–23:00</strong></div>","about.sun":"<div class=\"hours-line\"><span>Söndag</span><strong>12:00–21:00</strong></div>","about.reserve":"Boka ditt bord →",
      "menu.kicker":"FRÅN VÅRT KÖK","menu.title":"Utforska vår <i>meny</i>","menu.text":"Nylagade favoriter, från smårätter till härliga desserter.","menu.searchLabel":"Sök rätter","menu.hint":"Klicka på en rätt för mer information.","menu.searchPlaceholder":"Prova lax, pasta, dessert…","menu.meta":"16 rätter · priser i SEK","menu.allergy":"Fråga gärna personalen om allergier och specialkost.",
      "chef.kicker":"KOCKENS VAL","chef.title":"Oxfilé med potatisgratäng","chef.text":"Svensk oxfilé, krämig potatisgratäng, rödvinssås och rostade grönsaker.",
      "res.kicker":"BOKA BORD","res.title":"Boka ditt bord","res.text":"Välj datum, tid och antal gäster och granska sedan din bokning innan du skickar den.","res.name":"Namn *","res.phone":"Telefon *","res.email":"E-post *","res.guests":"Antal gäster *","res.date":"Datum *","res.time":"Tid *","res.requests":"Särskilda önskemål","res.select":"Välj","res.namePlaceholder":"Ditt namn","res.phonePlaceholder":"+46 ...","res.emailPlaceholder":"du@example.com","res.requestPlaceholder":"Födelsedag, allergier, barnstol, fönsterplats...","res.demo":"Demobokning","res.note":"Ingen bokning sparas online i denna version. Du granskar uppgifterna innan de skickas.","res.review":"Granska bokning →",
      "review.kicker":"KONTROLLERA DINA UPPGIFTER","review.title":"Din bokning","review.edit":"Ändra","review.email":"Skicka via e-post →","review.sms":"Skicka via SMS →","review.copy":"Kopiera uppgifter",
      "contact.kicker":"BESÖK OSS","contact.title":"Låt oss göra det <i>minnesvärt.</i>","footer.top":"Till toppen ↑",
      "email.prepared":"Ditt e-postprogram bör öppnas med bokningsuppgifterna ifyllda.","email.fallback":"Om inget händer: öppna ditt e-postprogram och skicka bokningsuppgifterna till","sms.prepared":"Din SMS-app bör öppnas med bokningsuppgifterna ifyllda.","copy.done":"Bokningsuppgifterna har kopierats.","copy.fail":"Kunde inte kopiera automatiskt. Markera och kopiera texten nedan.","subject":"Bokningsförfrågan","none":"Inga"
    },
    en:{"reservation.selectedDish":"Selected dish","reservation.removeDish":"Remove","reservation.noDish":"No selected dish","menu.view":"View details","menu.book":"Book a table","menu.close":"Close","menu.priceLabel":"Price","menu.servingLabel":"Serving","menu.servingValue":"Prepared to order","menu.allergyLabel":"Allergies","menu.allergyValue":"Please ask our staff",
      "top.open":"Open today 11:00–23:00","top.call":"Call +46 08 123 45 67","nav.home":"Home","nav.about":"About","nav.menu":"Menu","nav.reservation":"Reservation","nav.contact":"Contact","nav.book":"Book a table",
      "hero.kicker":"WELCOME TO TEST RESTAURANT","hero.title":"Good food.<br><i>Great moments.</i>","hero.text":"A modern dining experience where fresh ingredients, warm hospitality and memorable flavors meet.","hero.explore":"Explore menu",
      "about.kicker":"OUR STORY","about.title":"A place made for <i>good company.</i>","about.p1":"Test Restaurant is a modern demo concept built to show how a professional restaurant website can look and work.","about.p2":"Come for a relaxed lunch, a special dinner or simply a great dessert. Every detail is designed around an enjoyable experience.","about.mon":"Monday <b>Closed</b>","about.tueThu":"Tue–Thu <b>11:00–22:00</b>","about.fri":"<div class=\"hours-line\"><span>Fri–Sat</span><strong>11:00–23:00</strong></div>","about.sun":"<div class=\"hours-line\"><span>Sunday</span><strong>12:00–21:00</strong></div>","about.reserve":"Reserve your table →",
      "menu.kicker":"FROM OUR KITCHEN","menu.title":"Explore our <i>menu</i>","menu.text":"Freshly prepared favorites, from small plates to indulgent desserts.","menu.searchLabel":"Search dishes","menu.hint":"Click a dish to see more details.","menu.searchPlaceholder":"Try salmon, pasta, dessert…","menu.meta":"16 dishes · prices in SEK","menu.allergy":"Ask our staff about allergies and dietary requirements.",
      "chef.kicker":"CHEF'S PICK","chef.title":"Beef tenderloin with potato gratin","chef.text":"Swedish beef tenderloin, creamy potato gratin, red-wine sauce and roasted vegetables.",
      "res.kicker":"RESERVATIONS","res.title":"Reserve your table","res.text":"Choose your date, time and party size, then review your request before sending it.","res.name":"Full name *","res.phone":"Phone *","res.email":"Email *","res.guests":"Guests *","res.date":"Date *","res.time":"Time *","res.requests":"Special requests","res.select":"Select","res.namePlaceholder":"Your name","res.phonePlaceholder":"+46 ...","res.emailPlaceholder":"you@example.com","res.requestPlaceholder":"Birthday, allergies, high chair, window table...","res.demo":"Demo reservation","res.note":"No reservation is stored online in this version. You will review the details before sending.","res.review":"Review reservation →",
      "review.kicker":"CHECK YOUR DETAILS","review.title":"Your reservation","review.edit":"Edit","review.email":"Send by email →","review.sms":"Send by SMS →","review.copy":"Copy details",
      "contact.kicker":"COME VISIT","contact.title":"Let's make it <i>memorable.</i>","footer.top":"Back to top ↑",
      "email.prepared":"Your email app should open with the reservation details prepared.","email.fallback":"If nothing happens, open your email app and send the reservation details to","sms.prepared":"Your SMS app should open with the reservation details prepared.","copy.done":"The reservation details have been copied.","copy.fail":"Automatic copying failed. Select and copy the text below.","subject":"Table reservation request","none":"None"
    }
  };

  const categorySv={Starters:"Förrätter",Main:"Huvudrätter",Pasta:"Pasta",Vegetarian:"Vegetariskt",Burgers:"Burgare",Desserts:"Desserter",Drinks:"Dryck"};
  const dishSv={
    "Toast Skagen":["Toast Skagen","Handskalade räkor, dill, citron, pepparrot och rostat surdegsbröd."],
    "Burrata & Tomatoes":["Burrata & tomater","Krämig burrata, tomater, basilikaolja, rostade frön och havssalt."],
    "Crispy Calamari":["Krispig bläckfisk","Krispig bläckfisk, citron, persilja och rökt vitlöksaioli."],
    "Grilled Salmon":["Grillad lax","Grillad lax, krossad potatis, säsongens grönt och citronsmör."],
    "Beef Tenderloin":["Oxfilé","Svensk oxfilé, potatisgratäng, rödvinssås och rostade grönsaker."],
    "Herb Chicken":["Örtrostad kyckling","Örtrostad kycklingfilé, parmesanpotatis, haricots verts och sky."],
    "Truffle Mushroom Pasta":["Tryffelpasta med svamp","Tagliatelle, rostad svamp, parmesan, örter och tryffelgrädde."],
    "Prawn Linguine":["Linguine med räkor","Linguine, räkor, körsbärstomater, vitlök, chili, persilja och citron."],
    "Roasted Cauliflower":["Rostad blomkål","Rostad blomkål, örtlinser, tahini, granatäpple och rostade mandlar."],
    "Wild Mushroom Risotto":["Svamprisotto","Krämig risotto, skogssvamp, lagrad ost, örter och krispig schalottenlök."],
    "Classic House Burger":["Husets klassiska burgare","Svenskt nötkött, cheddar, sallad, tomat, pickles och husets dressing med pommes."],
    "Crème Brûlée":["Crème brûlée","Klassisk vanilj-crème brûlée med karamelliserat socker och färska bär."],
    "Chocolate Fondant":["Chokladfondant","Varm chokladfondant, vaniljglass och säsongens bär."],
    "Tiramisu":["Tiramisu","Espressodränkt sockerkaka, mascarponekräm och kakao."],
    "Fresh Lemonade":["Färsk lemonad","Färsk citron, mynta, kolsyrat vatten och en touch honung."],
    "Sparkling Elderflower":["Fläder & bubbel","Fläder, lime, mynta och kolsyrat vatten."]
  };

  function tr(key){return (T[currentLanguage]&&T[currentLanguage][key])||T.en[key]||key;}
  function applyLanguage(lang){
    currentLanguage=(lang==="en"?"en":"sv");
    localStorage.setItem("testRestaurantLanguage",currentLanguage);
    document.documentElement.lang=currentLanguage;
    document.querySelectorAll("[data-i18n]").forEach(el=>{el.innerHTML=tr(el.dataset.i18n)});
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el=>{el.placeholder=tr(el.dataset.i18nPlaceholder)});
    document.querySelectorAll("[data-lang]").forEach(b=>b.classList.toggle("active",b.dataset.lang===currentLanguage));
    document.querySelectorAll("#filters button").forEach(b=>{const cat=b.dataset.cat;b.textContent=currentLanguage==="sv"?(cat==="All"?"Alla":categorySv[cat]||cat):cat});
    if(typeof render==="function") render();
    if(reservationData) renderReview(reservationData);
  }
  document.querySelectorAll("[data-lang]").forEach(b=>b.addEventListener("click",()=>applyLanguage(b.dataset.lang)));

  // Patch menu rendering so dish/category names follow the selected language.
  const originalRender=render;
  render=function(){
    const q=currentQuery.trim().toLowerCase();
    const items=dishes.filter(d=>{
      const sv=dishSv[d[1]]||[];
      const haystack=`${d[1]} ${d[2]} ${d[0]} ${sv[0]||""} ${sv[1]||""} ${categorySv[d[0]]||""}`.toLowerCase();
      return (currentCat==="All"||d[0]===currentCat)&&(!q||haystack.includes(q));
    });
    grid.innerHTML=items.length?items.map(d=>{
      const title=currentLanguage==="sv"?(dishSv[d[1]]?.[0]||d[1]):d[1];
      const desc=currentLanguage==="sv"?(dishSv[d[1]]?.[1]||d[2]):d[2];
      const cat=currentLanguage==="sv"?(categorySv[d[0]]||d[0]):d[0];
      return `<article class="dish" tabindex="0" data-index="${dishes.indexOf(d)}"><div class="dishImage"><img loading="lazy" src="${d[4]}" alt="${title}"><span class="dishTag">${cat}</span><span class="viewDish">${currentLanguage==="sv"?"Visa detaljer":"View details"}</span></div><div><span class="price">${d[3]}</span><h3>${title}</h3><p>${desc}</p></div></article>`;
    }).join(""):`<div class="emptyMenu"><h3>${currentLanguage==="sv"?"Inga rätter hittades":"No dishes found"}</h3><p>${currentLanguage==="sv"?"Prova en annan sökning eller välj “Alla”.":"Try another search or choose “All”."}</p></div>`;
  };

  // Correct mobile navigation close behavior remains from V4; language buttons are outside nav.
  const today=new Date();
  dateEl.min=new Date(today.getTime()-today.getTimezoneOffset()*60000).toISOString().slice(0,10);
  const val=id=>document.getElementById(id).value.trim();
  const esc=x=>String(x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]));
  const dateLong=(value)=>{const dt=new Date(value+"T12:00:00");return dt.toLocaleDateString(currentLanguage==="sv"?"sv-SE":"en-US",{weekday:"long",year:"numeric",month:"long",day:"numeric"})};
  function buildBody(a){
  if (window.v9LocalizedDate) {
    const rawDateEl = document.getElementById("reservationDate") || document.getElementById("date");
    const rawReqEl = document.getElementById("specialRequests") || document.getElementById("requests");
    const rawDate = a.rawDate || (rawDateEl ? rawDateEl.value : "");
    const rawReq = (a.rawRequests !== undefined) ? a.rawRequests : (rawReqEl ? rawReqEl.value : "");
    a.rawDate = rawDate;
    a.rawRequests = rawReq;
    a.date = window.v9LocalizedDate(rawDate);
    a.requests = window.v9LocalizedRequests(rawReq);
  }
    if(currentLanguage==="sv") return `Hej Test Restaurant,\n\nJag vill gärna boka ett bord.\n\nNamn: ${a.name}\nTelefon: ${a.phone}\nE-post: ${a.email}\nAntal gäster: ${a.guests}\nDatum: ${a.date}\nTid: ${a.time}\nSärskilda önskemål: ${a.requests}\n\nTack!`;
    return `Hello Test Restaurant,\n\nI would like to request a table reservation.\n\nName: ${a.name}\nPhone: ${a.phone}\nEmail: ${a.email}\nGuests: ${a.guests}\nDate: ${a.date}\nTime: ${a.time}\nSpecial requests: ${a.requests}\n\nThank you.`;
  }
  function renderReview(a){
  if (window.v9LocalizedDate) {
    const rawDateEl = document.getElementById("reservationDate") || document.getElementById("date");
    const rawReqEl = document.getElementById("specialRequests") || document.getElementById("requests");
    const rawDate = a.rawDate || (rawDateEl ? rawDateEl.value : "");
    const rawReq = (a.rawRequests !== undefined) ? a.rawRequests : (rawReqEl ? rawReqEl.value : "");
    a.rawDate = rawDate;
    a.rawRequests = rawReq;
    a.date = window.v9LocalizedDate(rawDate);
    a.requests = window.v9LocalizedRequests(rawReq);
  }
    const displayDate=a.rawDate?dateLong(a.rawDate):a.date;
    const displayRequests=a.rawRequests?String(a.rawRequests).trim():(a.requests||"");
    const translatedRequests=displayRequests||tr("none");
    a.date=displayDate;
    a.requests=translatedRequests;
    details.innerHTML=`<div><span>${tr("res.name").replace(" *","")}</span><strong>${esc(a.name)}</strong></div><div><span>${tr("res.date").replace(" *","")}</span><strong>${esc(displayDate)}</strong></div><div><span>${tr("res.time").replace(" *","")}</span><strong>${esc(a.time)}</strong></div><div><span>${tr("res.guests").replace(" *","")}</span><strong>${esc(a.guests)}</strong></div><div><span>${tr("res.phone").replace(" *","")}</span><strong>${esc(a.phone)}</strong></div><div><span>${tr("res.email").replace(" *","")}</span><strong>${esc(a.email)}</strong></div><div class="wide"><span>${tr("res.requests")}</span><strong>${esc(translatedRequests)}</strong></div>`;
    review.dataset.subject=`${tr("subject")} - ${displayDate} ${a.time}`;
    review.dataset.body=buildBody(a);
  }
  form.addEventListener("submit",ev=>{
    ev.preventDefault();
    if(!form.checkValidity()){form.reportValidity();return;}
    reservationData={name:val("guestName"),phone:val("guestPhone"),email:val("guestEmail"),guests:val("guestCount"),rawDate:dateEl.value,date:dateLong(dateEl.value),time:val("reservationTime"),rawRequests:val("specialRequests"),requests:val("specialRequests")||tr("none")};
    renderReview(reservationData);
    message.hidden=true;help.hidden=true;form.hidden=true;review.hidden=false;
    review.scrollIntoView({behavior:"smooth",block:"center"});
  });
  editBtn.addEventListener("click",()=>{review.hidden=true;message.hidden=true;help.hidden=true;form.hidden=false;form.scrollIntoView({behavior:"smooth",block:"center"})});
  emailBtn.addEventListener("click",()=>{
    if(!reservationData)return;
    const subject=encodeURIComponent(review.dataset.subject),body=encodeURIComponent(review.dataset.body);
    const mailto=`mailto:${mailAddress}?subject=${subject}&body=${body}`;
    // Try the user's configured mail application. A visible fallback is shown immediately.
    window.location.href=mailto;
    message.textContent=tr("email.prepared");message.hidden=false;
    help.innerHTML=`${tr("email.fallback")} <strong>${mailAddress}</strong>.<br><button type="button" id="copyEmailDetails" class="secondary-btn">${tr("review.copy")}</button>`;
    help.hidden=false;
    document.getElementById("copyEmailDetails").addEventListener("click",copyReservationText);
  });
  smsBtn.addEventListener("click",()=>{
    if(!reservationData)return;
    const body=encodeURIComponent(review.dataset.body);
    const target=`sms:${reservationData.phone}?body=${body}`;
    const temp=document.createElement("a");
    temp.href=target;
    temp.style.display="none";
    document.body.appendChild(temp);
    temp.click();
    temp.remove();
    message.textContent=tr("sms.prepared");message.hidden=false;
    help.innerHTML=`${currentLanguage==="sv"?"Om Windows eller din enhet visar “Välj en app” kan du kopiera bokningsuppgifterna och öppna din SMS-app manuellt.":"If Windows or your device shows “Select an app”, copy the reservation details and open your SMS app manually."} <br><button type="button" id="copySmsDetails" class="secondary-btn">${tr("review.copy")}</button>`;
    help.hidden=false;
    document.getElementById("copySmsDetails").addEventListener("click",copyReservationText);
  });
  async function copyReservationText(){
    try{await navigator.clipboard.writeText(review.dataset.body);message.textContent=tr("copy.done");message.hidden=false;}
    catch(e){message.textContent=tr("copy.fail");message.hidden=false;}
  }
  copyBtn.addEventListener("click",copyReservationText);
  applyLanguage(currentLanguage);
})();


// Update dish modal text to the selected language without changing the V3/V4 visual design.
grid.addEventListener("click",function(e){
  const card=e.target.closest(".dish");
  if(!card)return;
  const d=dishes[Number(card.dataset.index)];
  if(currentLanguage==="sv"){
    const sv=dishSv[d[1]]||[d[1],d[2]];
    modalCategory.textContent=categorySv[d[0]]||d[0];
    modalTitle.textContent=sv[0];
    modalDescription.textContent=sv[1];
  }
});

/* V8_FIX_LAYER */
(function(){
  "use strict";

  function lang(){
    const s=(localStorage.getItem("testRestaurantLanguage")||
             localStorage.getItem("restaurantLanguage")||
             localStorage.getItem("language")||
             document.documentElement.lang||"sv").toLowerCase();
    return s.startsWith("en")?"en":"sv";
  }

  function fmtDate(raw){
    if(!raw) return "";
    const d=new Date(raw+"T12:00:00");
    if(Number.isNaN(d.getTime())) return raw;
    return new Intl.DateTimeFormat(lang()==="en"?"en-GB":"sv-SE",{
      weekday:"long",day:"numeric",month:"long",year:"numeric"
    }).format(d);
  }

  function fmtRequests(raw){
    return String(raw||"").trim() || (lang()==="en"?"None":"Inga");
  }

  window.v8FormatDate=fmtDate;
  window.v8FormatRequests=fmtRequests;
  window.v8ReservationRaw=null;

  window.v8RememberReservation=function(a){
    if(!a) return;
    window.v8ReservationRaw={
      name:a.name||"",
      phone:a.phone||"",
      email:a.email||"",
      guests:a.guests||"",
      rawDate:a.rawDate||a.dateRaw||"",
      time:a.time||"",
      rawRequests:(a.rawRequests!==undefined?a.rawRequests:"")
    };
  if (window.v8RememberReservation) window.v8RememberReservation(reservationData);
  };

  window.v8RefreshReview=function(){
    const a=window.v8ReservationRaw;
    if(!a) return;

    const dateText=fmtDate(a.rawDate);
    const reqText=fmtRequests(a.rawRequests);

    document.querySelectorAll("[data-reservation-date],[data-review-date],#reviewDate,#reservationReviewDate")
      .forEach(el=>el.textContent=dateText);

    document.querySelectorAll("[data-reservation-requests],[data-review-requests],#reviewRequests,#reservationReviewRequests")
      .forEach(el=>el.textContent=reqText);

    if(typeof window.renderReview==="function"){
      try{
        window.renderReview({
          name:a.name,phone:a.phone,email:a.email,guests:a.guests,
          rawDate:a.rawDate,date:dateText,time:a.time,
          rawRequests:a.rawRequests,requests:reqText
        });
      }catch(e){}
    }
  };

  document.addEventListener("click",function(e){
    const b=e.target.closest("[data-language],[data-lang],.language-switch button,.lang-switch button,.language-btn,.lang-btn");
    if(!b) return;

    const chosen=b.getAttribute("data-language")||
                 b.getAttribute("data-lang")||
                 (/english/i.test(b.textContent)?"en":(/svenska/i.test(b.textContent)?"sv":""));

    if(chosen){
      try{localStorage.setItem("testRestaurantLanguage",chosen)}catch(e){}
      document.documentElement.lang=chosen;
    }
    setTimeout(window.v8RefreshReview,0);
  });

  document.addEventListener("click",function(e){
    const a=e.target.closest('a[href^="sms:"]');
    if(!a) return;
    const ua=navigator.userAgent||"";
    const windowsDesktop=/Windows NT/i.test(ua)&&!/Mobile|Android/i.test(ua);
    if(!windowsDesktop) return;

    e.preventDefault();
    const text=lang()==="en"
      ?"SMS links normally work on a mobile phone. On this Windows computer, copy the reservation details instead."
      :"SMS-länkar fungerar normalt på mobil. På den här Windows-datorn kan du kopiera bokningsuppgifterna i stället.";

    const box=document.getElementById("reservationHelp")||
              document.getElementById("help")||
              document.getElementById("reservationMessage")||
              document.getElementById("message");

    if(box){box.textContent=text;box.hidden=false}
    else alert(text);
  },true);
})();


/* ===== Version 9 canonical language refresh ===== */
(function(){
  "use strict";

  function currentLang(){
    const s=(localStorage.getItem("testRestaurantLanguage")||
             localStorage.getItem("restaurantLanguage")||
             localStorage.getItem("language")||
             document.documentElement.lang||"sv").toLowerCase();
    return s.startsWith("en") ? "en" : "sv";
  }

  function localizedDate(raw){
    if(!raw) return "";
    const d=new Date(raw+"T12:00:00");
    if(Number.isNaN(d.getTime())) return raw;
    return new Intl.DateTimeFormat(currentLang()==="en"?"en-GB":"sv-SE",{
      weekday:"long", day:"numeric", month:"long", year:"numeric"
    }).format(d);
  }

  function localizedRequests(raw){
    return String(raw||"").trim() || (currentLang()==="en" ? "None" : "Inga");
  }

  function getRawDate(){
    const el=document.getElementById("reservationDate") || document.getElementById("date");
    return el ? el.value : "";
  }

  function getRawRequests(){
    const el=document.getElementById("specialRequests") || document.getElementById("requests");
    return el ? el.value : "";
  }

  window.v9LocalizedDate=localizedDate;
  window.v9LocalizedRequests=localizedRequests;

  window.v9RefreshReview=function(){
    const rawDate=getRawDate();
    const rawRequests=getRawRequests();

    const dateText=localizedDate(rawDate);
    const requestText=localizedRequests(rawRequests);

    document.querySelectorAll(
      "[data-reservation-date],[data-review-date],#reviewDate,#reservationReviewDate"
    ).forEach(el=>el.textContent=dateText);

    document.querySelectorAll(
      "[data-reservation-requests],[data-review-requests],#reviewRequests,#reservationReviewRequests"
    ).forEach(el=>el.textContent=requestText);

    if(typeof reservationData!=="undefined" && reservationData){
      reservationData.rawDate=rawDate || reservationData.rawDate || "";
      reservationData.rawRequests=rawRequests;
      reservationData.date=localizedDate(reservationData.rawDate);
      reservationData.requests=localizedRequests(reservationData.rawRequests);

      if(typeof renderReview==="function"){
        try{ renderReview(reservationData); }catch(e){}
      } else if(typeof window.renderReview==="function"){
        try{ window.renderReview(reservationData); }catch(e){}
      }
    }
  };

  document.addEventListener("click",function(e){
    const btn=e.target.closest(
      "[data-language],[data-lang],.language-switch button,.lang-switch button,.language-btn,.lang-btn"
    );
    if(!btn) return;
    setTimeout(window.v9RefreshReview,0);
  });
})();


/* V10_FIXED_LANGUAGE_SELECTOR */
(function(){
  const KEY="testRestaurantLanguage";

  function canonicalLang(){
    const saved=localStorage.getItem(KEY);
    if(saved) return saved==="en" ? "en" : "sv";

    // V7/V9 may use a different key. Respect it only if the user explicitly chose it.
    const legacy=localStorage.getItem("restaurantLanguage") || localStorage.getItem("language");
    if(legacy==="en" || legacy==="sv"){
      localStorage.setItem(KEY, legacy);
      return legacy;
    }

    localStorage.setItem(KEY,"sv");
    return "sv";
  }

  function syncButtons(lang){
    document.querySelectorAll('[data-lang="sv"],[data-lang="en"],[data-language="sv"],[data-language="en"]')
      .forEach(btn=>{
        const value=btn.getAttribute("data-lang") || btn.getAttribute("data-language");
        btn.classList.toggle("active", value===lang);
        btn.setAttribute("aria-pressed", value===lang ? "true" : "false");
      });
  }

  function useExistingLanguageEngine(lang){
    // Trigger the original header language button so all existing translations
    // continue to use the site's tested V9 translation logic.
    const candidates=[...document.querySelectorAll('[data-lang="'+lang+'"]')];
    const original=candidates.find(b=>!b.closest("#reservationLangSwitch"));
    if(original){
      original.click();
      return true;
    }
    return false;
  }

  document.addEventListener("DOMContentLoaded",()=>{
    const lang=canonicalLang();
    document.documentElement.lang=lang;
    syncButtons(lang);

    // On a true first visit, make the existing site translation engine render Swedish.
    setTimeout(()=>{
      const current=document.documentElement.lang;
      if(lang==="sv" && current!=="sv") useExistingLanguageEngine("sv");
      syncButtons(lang);
    },0);
  });

  document.addEventListener("click",e=>{
    const btn=e.target.closest("#reservationLangSwitch [data-lang]");
    if(!btn) return;

    const lang=btn.getAttribute("data-lang")==="en" ? "en" : "sv";
    localStorage.setItem(KEY,lang);
    localStorage.setItem("restaurantLanguage",lang);
    localStorage.setItem("language",lang);
    document.documentElement.lang=lang;

    // Use original tested language handler.
    useExistingLanguageEngine(lang);
    syncButtons(lang);

    if(window.v9RefreshReview) setTimeout(window.v9RefreshReview,0);
  });

  // Keep both selectors synchronized when header is used.
  document.addEventListener("click",e=>{
    const btn=e.target.closest('[data-lang="sv"],[data-lang="en"]');
    if(!btn || btn.closest("#reservationLangSwitch")) return;
    const lang=btn.getAttribute("data-lang")==="en" ? "en" : "sv";
    localStorage.setItem(KEY,lang);
    syncButtons(lang);
  });
})();

/* V11_CARD_LANGUAGE_SWITCH */
(function(){
  "use strict";
  const KEY="testRestaurantLanguage";

  function syncCardLanguageButtons(lang){
    document.querySelectorAll('#reservationLangSwitch [data-lang]').forEach(btn=>{
      const value=btn.getAttribute("data-lang");
      btn.classList.toggle("active", value===lang);
      btn.setAttribute("aria-pressed", value===lang ? "true" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", function(){
    const lang=(localStorage.getItem(KEY)||"sv")==="en" ? "en" : "sv";
    syncCardLanguageButtons(lang);
  });

  document.addEventListener("click", function(e){
    const btn=e.target.closest('#reservationLangSwitch [data-lang]');
    if(!btn) return;

    const lang=btn.getAttribute("data-lang")==="en" ? "en" : "sv";
    localStorage.setItem(KEY,lang);

    // Click original header button to use the already-tested translation engine.
    const original=[...document.querySelectorAll('[data-lang="'+lang+'"]')]
      .find(x=>!x.closest("#reservationLangSwitch"));

    if(original){
      original.click();
    }

    syncCardLanguageButtons(lang);

    if(window.v9RefreshReview){
      setTimeout(window.v9RefreshReview,0);
    }
  });

  document.addEventListener("click", function(e){
    const btn=e.target.closest('[data-lang="sv"],[data-lang="en"]');
    if(!btn || btn.closest("#reservationLangSwitch")) return;
    const lang=btn.getAttribute("data-lang")==="en" ? "en" : "sv";
    syncCardLanguageButtons(lang);
  });
})();

/* V12_FRESH_LANGUAGE_STATE */
(function(){
  "use strict";

  const V12_KEY="testRestaurantLanguageV12";

  function currentV12Lang(){
    const saved=localStorage.getItem(V12_KEY);
    return saved==="en" ? "en" : "sv";
  }

  function syncV12Buttons(lang){
    document.querySelectorAll("[data-v12-lang]").forEach(btn=>{
      const value=btn.getAttribute("data-v12-lang");
      btn.classList.toggle("active", value===lang);
      btn.setAttribute("aria-pressed", value===lang ? "true" : "false");
    });
  }

  function findOriginalHeaderButton(lang){
    return [...document.querySelectorAll('[data-lang="'+lang+'"]')]
      .find(btn=>!btn.closest("#formLangSwitch") && !btn.closest("#reviewLangSwitch"));
  }

  function applyV12Lang(lang){
    lang = lang==="en" ? "en" : "sv";
    localStorage.setItem(V12_KEY, lang);

    // Keep old site language storage synchronized so the existing translation engine works.
    localStorage.setItem("testRestaurantLanguage", lang);
    localStorage.setItem("restaurantLanguage", lang);
    localStorage.setItem("language", lang);
    document.documentElement.lang = lang;

    const original = findOriginalHeaderButton(lang);
    if(original){
      original.click();
    } else if(typeof window.applyLanguage==="function"){
      try{ window.applyLanguage(lang); }catch(e){}
    } else if(typeof applyLanguage==="function"){
      try{ applyLanguage(lang); }catch(e){}
    }

    syncV12Buttons(lang);

    if(window.v9RefreshReview){
      setTimeout(window.v9RefreshReview,0);
    }
  }

  document.addEventListener("DOMContentLoaded",function(){
    // First ever V12 visit defaults to Swedish, regardless of older V9/V10/V11 keys.
    if(!localStorage.getItem(V12_KEY)){
      localStorage.setItem(V12_KEY,"sv");
    }
    const lang=currentV12Lang();

    // Override any older version's stored language with the V12 choice.
    localStorage.setItem("testRestaurantLanguage",lang);
    localStorage.setItem("restaurantLanguage",lang);
    localStorage.setItem("language",lang);
    document.documentElement.lang=lang;

    syncV12Buttons(lang);

    setTimeout(function(){
      const original=findOriginalHeaderButton(lang);
      if(original) original.click();
      syncV12Buttons(lang);
      if(window.v9RefreshReview) window.v9RefreshReview();
    },0);
  });

  document.addEventListener("click",function(e){
    const btn=e.target.closest("[data-v12-lang]");
    if(!btn) return;
    e.preventDefault();
    applyV12Lang(btn.getAttribute("data-v12-lang"));
  });

  // Keep V12 controls synchronized when the header control is used.
  document.addEventListener("click",function(e){
    const btn=e.target.closest('[data-lang="sv"],[data-lang="en"]');
    if(!btn) return;
    const lang=btn.getAttribute("data-lang")==="en" ? "en" : "sv";
    localStorage.setItem(V12_KEY,lang);
    syncV12Buttons(lang);
  });

  window.v12ApplyLanguage=applyV12Lang;
})();

/* V14_RESERVATION_REFERENCE */
(function(){
  "use strict";

  const REF_KEY="testRestaurantReferenceV14";
  let currentReference=sessionStorage.getItem(REF_KEY) || "";

  function lang(){
    const s=(localStorage.getItem("testRestaurantLanguageV12") ||
             localStorage.getItem("testRestaurantLanguage") ||
             document.documentElement.lang || "sv").toLowerCase();
    return s.startsWith("en") ? "en" : "sv";
  }

  function makeReference(){
    const d=new Date();
    const y=d.getFullYear().toString().slice(-2);
    const m=String(d.getMonth()+1).padStart(2,"0");
    const day=String(d.getDate()).padStart(2,"0");
    const rand=Math.floor(1000+Math.random()*9000);
    return `TR-${y}${m}${day}-${rand}`;
  }

  function ensureReference(){
    if(!currentReference){
      currentReference=makeReference();
      sessionStorage.setItem(REF_KEY,currentReference);
    }
    return currentReference;
  }

  function renderReference(){
    const box=document.getElementById("reservationReference");
    if(!box) return;
    const ref=ensureReference();
    box.textContent=(lang()==="en" ? "Reservation reference: " : "Bokningsreferens: ") + ref;
    box.hidden=false;
  }

  function updateNewButton(){
    const btn=document.getElementById("newReservation");
    if(!btn) return;
    btn.textContent=lang()==="en" ? "New reservation" : "Ny bokning";
  }

  function refreshV14(){
    renderReference();
    updateNewButton();
  }

  // When reservation review becomes visible, ensure a reference is shown.
  const review=document.getElementById("reservationReview");
  if(review){
    const obs=new MutationObserver(()=>{
      if(!review.hidden) refreshV14();
    });
    obs.observe(review,{attributes:true,attributeFilter:["hidden","class","style"]});
  }

  document.addEventListener("click",function(e){
    const langBtn=e.target.closest("[data-v12-lang],[data-lang]");
    if(langBtn) setTimeout(refreshV14,0);
  });

  document.addEventListener("click",function(e){
    const btn=e.target.closest("#newReservation");
    if(!btn) return;

    const form=document.getElementById("reservationForm");
    const review=document.getElementById("reservationReview");
    const sent=document.getElementById("reservationSent");
    const help=document.getElementById("communicationHelp");

    if(form){
      form.reset();
      form.hidden=false;
    }
    if(review) review.hidden=true;
    if(sent) sent.hidden=true;
    if(help) help.hidden=true;

    currentReference="";
    sessionStorage.removeItem(REF_KEY);

    const name=document.getElementById("guestName");
    if(name) name.focus();

    const section=document.getElementById("reservation");
    if(section) section.scrollIntoView({behavior:"smooth",block:"start"});
  });

  // Extend copied/email/SMS body if buildBody is global.
  const oldBuild=window.buildBody;
  if(typeof oldBuild==="function"){
    window.buildBody=function(a){
      const body=oldBuild(a);
      const ref=ensureReference();
      return body + "\n" + (lang()==="en" ? "Reservation reference: " : "Bokningsreferens: ") + ref;
    };
  }

  document.addEventListener("DOMContentLoaded",updateNewButton);
  window.v14ReservationReference=ensureReference;
})();




/* V16_STRICT_RESERVATION_VALIDATION */
(function(){
  "use strict";

  function lang(){
    const s=(localStorage.getItem("testRestaurantLanguageV12") ||
             localStorage.getItem("testRestaurantLanguage") ||
             document.documentElement.lang || "sv").toLowerCase();
    return s.startsWith("en") ? "en" : "sv";
  }

  function t(key){
    const en=lang()==="en";
    const dict={
      required: en ? "Please complete all required fields before continuing." :
                     "Fyll i alla obligatoriska fält innan du fortsätter.",
      email: en ? "Please enter a valid email address, for example name@example.com." :
                  "Ange en giltig e-postadress, till exempel namn@example.com.",
      phone: en ? "Please enter a valid phone number with 7–15 digits." :
                  "Ange ett giltigt telefonnummer med 7–15 siffror.",
      past: en ? "Please choose today or a future date." :
                 "Välj dagens datum eller ett framtida datum.",
      date: en ? "Please enter or select a valid date." :
                 "Ange eller välj ett giltigt datum.",
      guests: en ? "Please choose the number of guests." :
                   "Välj antal gäster."
    };
    return dict[key] || "";
  }

  function localTodayString(){
    const d=new Date();
    const local=new Date(d.getTime()-d.getTimezoneOffset()*60000);
    return local.toISOString().slice(0,10);
  }

  function setMinDate(){
    const date=document.getElementById("reservationDate");
    if(date) date.min=localTodayString();
  }

  function clearErrors(){
    document.querySelectorAll(".field-error").forEach(el=>el.classList.remove("field-error"));
    const box=document.getElementById("validationMessage");
    if(box){
      box.hidden=true;
      box.textContent="";
    }
  }

  function showError(message, el){
    const box=document.getElementById("validationMessage");
    if(box){
      box.textContent=message;
      box.hidden=false;
    }
    if(el){
      el.classList.add("field-error");
      try{ el.focus(); }catch(e){}
    }
  }

  function validEmail(value){
    value=String(value||"").trim();
    if(value.length<6 || value.length>254) return false;
    const at=value.indexOf("@");
    if(at<=0 || at!==value.lastIndexOf("@")) return false;
    const local=value.slice(0,at);
    const domain=value.slice(at+1);
    if(local.length>64 || !domain.includes(".")) return false;
    if(local.startsWith(".") || local.endsWith(".") || local.includes("..")) return false;
    if(domain.startsWith(".") || domain.endsWith(".") || domain.includes("..")) return false;

    const labels=domain.split(".");
    if(labels.some(x=>!x || x.length>63 || x.startsWith("-") || x.endsWith("-"))) return false;
    if(labels.some(x=>!/^[A-Za-z0-9-]+$/.test(x))) return false;

    const tld=labels[labels.length-1];
    if(!/^[A-Za-z]{2,63}$/.test(tld)) return false;

    return /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+$/.test(local);
  }

  function validPhone(value){
    value=String(value||"").trim();
    if(!/^[+\d\s().-]+$/.test(value)) return false;
    const digits=value.replace(/\D/g,"");
    return digits.length>=7 && digits.length<=15;
  }

  function parseIsoDateStrict(value){
    if(!/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
    const [y,m,d]=value.split("-").map(Number);
    if(y<1900 || y>2100 || m<1 || m>12 || d<1 || d>31) return null;
    const dt=new Date(y,m-1,d);
    if(dt.getFullYear()!==y || dt.getMonth()!==m-1 || dt.getDate()!==d) return null;
    return dt;
  }

  function validate(){
    clearErrors();

    const fields=[
      document.getElementById("guestName"),
      document.getElementById("guestPhone"),
      document.getElementById("guestEmail"),
      document.getElementById("reservationDate"),
      document.getElementById("reservationTime"),
      document.getElementById("guestCount")
    ].filter(Boolean);

    for(const el of fields){
      if(!String(el.value || "").trim()){
        showError(t("required"), el);
        return false;
      }
    }

    const guests=document.getElementById("guestCount");
    if(guests && (!guests.value || Number(guests.value)<1 || Number(guests.value)>20)){
      showError(t("guests"), guests);
      return false;
    }

    const email=document.getElementById("guestEmail");
    if(email && !validEmail(email.value)){
      showError(t("email"), email);
      return false;
    }

    const phone=document.getElementById("guestPhone");
    if(phone && !validPhone(phone.value)){
      showError(t("phone"), phone);
      return false;
    }

    const date=document.getElementById("reservationDate");
    if(date){
      const parsed=parseIsoDateStrict(date.value);
      if(!parsed){
        showError(t("date"), date);
        return false;
      }

      const today=parseIsoDateStrict(localTodayString());
      if(parsed<today){
        showError(t("past"), date);
        return false;
      }
    }

    return true;
  }

  document.addEventListener("DOMContentLoaded",setMinDate);

  document.addEventListener("submit",function(e){
    const form=e.target.closest("#reservationForm");
    if(!form) return;
    if(!validate()){
      e.preventDefault();
      e.stopImmediatePropagation();
      return false;
    }
  }, true);

  document.addEventListener("input",function(e){
    if(e.target.closest("#reservationForm")){
      e.target.classList.remove("field-error");
    }
  });

  document.addEventListener("change",function(e){
    if(e.target.closest("#reservationForm")){
      e.target.classList.remove("field-error");
    }
  });

  document.addEventListener("click",function(e){
    if(e.target.closest("[data-v12-lang],[data-lang]")){
      setTimeout(()=>{
        const box=document.getElementById("validationMessage");
        if(box && !box.hidden) validate();
      },0);
    }
  });

  // Defensive protection: if some older handler tries to show the review with a bad date,
  // immediately stop it and return to the form with a localized error.
  const review=document.getElementById("reservationReview");
  if(review){
    const obs=new MutationObserver(()=>{
      if(review.hidden) return;
      const date=document.getElementById("reservationDate");
      const parsed=date ? parseIsoDateStrict(date.value) : null;
      if(!parsed){
        review.hidden=true;
        const form=document.getElementById("reservationForm");
        if(form) form.hidden=false;
        showError(t("date"), date);
      }
    });
    obs.observe(review,{attributes:true,attributeFilter:["hidden","style","class"]});
  }

  window.v16ValidateReservation=validate;
})();

/* V18_SESSION_LANGUAGE_DEFAULT */
(function(){
  "use strict";

  const SESSION_KEY="testRestaurantLanguageSessionV18";

  function setStores(lang){
    localStorage.setItem("testRestaurantLanguageV12",lang);
    localStorage.setItem("testRestaurantLanguage",lang);
    localStorage.setItem("restaurantLanguage",lang);
    localStorage.setItem("language",lang);
    document.documentElement.lang=lang;
  }

  function originalButton(lang){
    return [...document.querySelectorAll('[data-lang="'+lang+'"]')]
      .find(btn=>!btn.closest("#formLangSwitch") && !btn.closest("#reviewLangSwitch"));
  }

  function syncReservationButtons(lang){
    document.querySelectorAll("[data-v12-lang]").forEach(btn=>{
      const active=btn.getAttribute("data-v12-lang")===lang;
      btn.classList.toggle("active",active);
      btn.setAttribute("aria-pressed",active ? "true" : "false");
    });
  }

  function apply(lang){
    lang=lang==="en" ? "en" : "sv";
    sessionStorage.setItem(SESSION_KEY,lang);
    setStores(lang);

    const btn=originalButton(lang);
    if(btn) btn.click();

    syncReservationButtons(lang);

    if(window.v17RefreshTimes) setTimeout(window.v17RefreshTimes,0);
    if(window.v9RefreshReview) setTimeout(window.v9RefreshReview,0);
  }

  document.addEventListener("DOMContentLoaded",function(){
    // A fresh browser/tab session must always begin in Swedish.
    if(!sessionStorage.getItem(SESSION_KEY)){
      sessionStorage.setItem(SESSION_KEY,"sv");
    }
    setTimeout(function(){
      apply(sessionStorage.getItem(SESSION_KEY) || "sv");
    },0);
  });

  document.addEventListener("click",function(e){
    const btn=e.target.closest("[data-v12-lang],[data-lang]");
    if(!btn) return;
    const lang=btn.getAttribute("data-v12-lang") || btn.getAttribute("data-lang");
    if(lang==="sv" || lang==="en"){
      sessionStorage.setItem(SESSION_KEY,lang);
    }
  });

  window.v18ApplySessionLanguage=apply;
})();

/* V20_ALWAYS_START_SWEDISH */
(function(){
  "use strict";

  function forceSwedish(){
    const lang="sv";

    localStorage.setItem("testRestaurantLanguageV12",lang);
    localStorage.setItem("testRestaurantLanguage",lang);
    localStorage.setItem("restaurantLanguage",lang);
    localStorage.setItem("language",lang);

    // Also override V18's session preference on each page load.
    sessionStorage.setItem("testRestaurantLanguageSessionV18",lang);
    document.documentElement.lang=lang;

    const headerButton=[...document.querySelectorAll('[data-lang="sv"]')]
      .find(btn=>!btn.closest("#formLangSwitch") && !btn.closest("#reviewLangSwitch"));

    if(headerButton) headerButton.click();

    document.querySelectorAll("[data-v12-lang]").forEach(btn=>{
      const active=btn.getAttribute("data-v12-lang")==="sv";
      btn.classList.toggle("active",active);
      btn.setAttribute("aria-pressed",active ? "true" : "false");
    });

    if(window.v17RefreshTimes) setTimeout(window.v17RefreshTimes,0);
    if(window.v9RefreshReview) setTimeout(window.v9RefreshReview,0);
  }

  document.addEventListener("DOMContentLoaded",function(){
    // Run after older language initialization code so Swedish wins on every load.
    setTimeout(forceSwedish,25);
  });
})();


/* V21_OPENING_HOURS_AND_TIMES */
(function(){
  "use strict";

  function lang(){
    const s=(document.documentElement.lang || "sv").toLowerCase();
    return s.startsWith("en") ? "en" : "sv";
  }

  function parseDate(){
    const el=document.getElementById("reservationDate");
    if(!el || !/^\d{4}-\d{2}-\d{2}$/.test(el.value)) return null;
    const [y,m,d]=el.value.split("-").map(Number);
    const dt=new Date(y,m-1,d);
    if(dt.getFullYear()!==y || dt.getMonth()!==m-1 || dt.getDate()!==d) return null;
    return dt;
  }

  function buildTimes(startHour,startMin,endHour,endMin){
    const result=[];
    let minutes=startHour*60+startMin;
    const end=endHour*60+endMin;

    // 30-minute slots; last selectable time is 30 min before closing.
    while(minutes <= end-30){
      const h=Math.floor(minutes/60);
      const m=minutes%60;
      result.push(String(h).padStart(2,"0")+":"+String(m).padStart(2,"0"));
      minutes += 30;
    }
    return result;
  }

  function allowedTimes(date){
    if(!date) return [];

    const day=date.getDay(); // 0 Sun, 1 Mon, ... 6 Sat

    if(day===1) return []; // Monday closed
    if(day>=2 && day<=4) return buildTimes(11,0,22,0); // Tue-Thu 11:00-22:00
    if(day===5 || day===6) return buildTimes(11,0,23,0); // Fri-Sat 11:00-23:00
    if(day===0) return buildTimes(12,0,21,0); // Sunday 12:00-21:00

    return [];
  }

  function refreshTimes(){
    const select=document.getElementById("reservationTime");
    const hint=document.getElementById("timeAvailabilityHint");
    if(!select) return;

    const previous=select.value;
    const date=parseDate();
    const times=allowedTimes(date);

    select.innerHTML="";

    const placeholder=document.createElement("option");
    placeholder.value="";
    placeholder.textContent=lang()==="en" ? "Select time" : "Välj tid";
    select.appendChild(placeholder);

    times.forEach(time=>{
      const option=document.createElement("option");
      option.value=time;
      option.textContent=time;
      select.appendChild(option);
    });

    select.disabled=!!date && times.length===0;

    if(times.includes(previous)){
      select.value=previous;
    }

    if(hint){
      if(!date){
        hint.textContent=lang()==="en"
          ? "Select a date to see available reservation times."
          : "Välj ett datum för att se tillgängliga bokningstider.";
      }else if(times.length===0){
        hint.textContent=lang()==="en"
          ? "Closed on Mondays — please choose another date."
          : "Stängt på måndagar – välj ett annat datum.";
      }else{
        hint.textContent=lang()==="en"
          ? "Times are based on the restaurant's opening hours."
          : "Tiderna följer restaurangens öppettider.";
      }
    }
  }

  document.addEventListener("DOMContentLoaded",refreshTimes);

  document.addEventListener("change",function(e){
    if(e.target && e.target.id==="reservationDate"){
      refreshTimes();
    }
  });

  document.addEventListener("click",function(e){
    if(e.target.closest("[data-v12-lang],[data-lang]")){
      setTimeout(refreshTimes,0);
    }
  });

  window.v21RefreshTimes=refreshTimes;
})();

/* V25_DYNAMIC_TODAY_OPEN_STATUS */
(function(){
  "use strict";

  function currentLang(){
    const lang=(document.documentElement.lang || "sv").toLowerCase();
    return lang.startsWith("en") ? "en" : "sv";
  }

  function todayText(){
    const day=(new Date()).getDay(); // Sun=0, Mon=1 ... Sat=6
    const en=currentLang()==="en";

    if(day===1){
      return en ? "Closed today" : "Stängt idag";
    }
    if(day>=2 && day<=4){
      return en ? "Open today 11:00–22:00" : "Öppet idag 11:00–22:00";
    }
    if(day===5 || day===6){
      return en ? "Open today 11:00–23:00" : "Öppet idag 11:00–23:00";
    }
    return en ? "Open today 12:00–21:00" : "Öppet idag 12:00–21:00";
  }

  function refreshTodayOpenStatus(){
    const el=document.getElementById("todayOpenStatus");
    if(el) el.textContent=todayText();
  }

  document.addEventListener("DOMContentLoaded",function(){
    setTimeout(refreshTodayOpenStatus,40);
  });

  document.addEventListener("click",function(e){
    if(e.target.closest("[data-v12-lang],[data-lang]")){
      setTimeout(refreshTodayOpenStatus,20);
    }
  });

  window.v25RefreshTodayOpenStatus=refreshTodayOpenStatus;
})();

/* V27_RESERVATION_READY_CARD_FIX */
(function(){
  "use strict";

  function lang(){
    const l=(document.documentElement.lang || "sv").toLowerCase();
    return l.startsWith("en") ? "en" : "sv";
  }

  function byId(id){ return document.getElementById(id); }

  function firstExisting(ids){
    for(const id of ids){
      const el=byId(id);
      if(el) return el;
    }
    return null;
  }

  function elementValue(el){
    if(!el) return "";
    if("value" in el && String(el.value).trim()) return String(el.value).trim();
    return String(el.textContent || "").trim();
  }

  function readGuestCount(){
    const direct = firstExisting([
      "reservationGuests",
      "guests",
      "guestCount",
      "numberOfGuests"
    ]);
    let value = elementValue(direct);

    if(!value){
      const select = document.querySelector(
        '#reservationForm select[name*="guest" i], select[id*="guest" i]'
      );
      value = elementValue(select);
    }

    return value || "—";
  }

  function readReference(){
    const el = firstExisting([
      "reservationReference",
      "reviewReference",
      "reservationRef"
    ]);

    let value = elementValue(el);
    if(!value) return "—";

    // Keep only the actual reference code if label text is embedded.
    const match = value.match(/TR-\d{6}-\d+/i);
    if(match) return match[0].toUpperCase();

    value = value
      .replace(/^reservation reference\s*:\s*/i, "")
      .replace(/^bokningsreferens\s*:\s*/i, "")
      .replace(/^bokningsnummer\s*:\s*/i, "")
      .trim();

    return value || "—";
  }

  function readDate(){
    const el = firstExisting(["reservationDate","date"]);
    return elementValue(el);
  }

  function readTime(){
    const el = firstExisting(["reservationTime","time"]);
    return elementValue(el) || "—";
  }

  function formatDate(value){
    if(!/^\d{4}-\d{2}-\d{2}$/.test(value)) return value || "—";
    const [y,m,d]=value.split("-").map(Number);
    const dt=new Date(y,m-1,d);
    try{
      return new Intl.DateTimeFormat(lang()==="en" ? "en-GB" : "sv-SE", {
        year:"numeric", month:"long", day:"numeric"
      }).format(dt);
    }catch{
      return value;
    }
  }

  function updateCard(){
    const card=byId("reservationReadyCard");
    if(!card) return;

    const en=lang()==="en";

    byId("reservationReadyTitle").textContent=en
      ? "Your reservation request is ready"
      : "Din bokningsförfrågan är klar";

    byId("reservationReadySubtitle").textContent=en
      ? "Check the details below before sending them."
      : "Kontrollera uppgifterna nedan innan du skickar dem.";

    byId("readyDateLabel").textContent=en ? "Date" : "Datum";
    byId("readyTimeLabel").textContent=en ? "Time" : "Tid";
    byId("readyGuestsLabel").textContent=en ? "Guests" : "Gäster";
    byId("readyRefLabel").textContent=en ? "Reservation no." : "Bokningsnummer";

    byId("readyDateValue").textContent=formatDate(readDate());
    byId("readyTimeValue").textContent=readTime();
    byId("readyGuestsValue").textContent=readGuestCount();
    byId("readyRefValue").textContent=readReference();

    const review=card.parentElement;
    const visible=review && !review.hidden && getComputedStyle(review).display!=="none";
    card.hidden=!visible;
  }

  document.addEventListener("DOMContentLoaded",function(){
    setTimeout(updateCard,80);
  });

  document.addEventListener("click",function(e){
    if(
      e.target.closest("[data-v12-lang],[data-lang]") ||
      e.target.closest("#reservationForm button, #reservationReview button, button")
    ){
      setTimeout(updateCard,80);
    }
  });

  document.addEventListener("change",function(e){
    if(e.target && e.target.closest("#reservationForm")){
      setTimeout(updateCard,20);
    }
  });

  const observer=new MutationObserver(function(){
    setTimeout(updateCard,20);
  });

  document.addEventListener("DOMContentLoaded",function(){
    const card=byId("reservationReadyCard");
    if(card && card.parentElement){
      observer.observe(card.parentElement,{
        attributes:true,
        childList:true,
        subtree:true,
        attributeFilter:["hidden","class","style"]
      });
    }
  });

  window.v27RefreshReservationCard=updateCard;
})();


// V29_SELECTED_DISH_CONNECTION
let selectedDishV29 = null;

function setSelectedDishV29(dish){
  if(!dish){
    selectedDishV29 = null;
  }else{
    const sv = (typeof dishSv!=="undefined" && dishSv[dish[1]]) || null;
    selectedDishV29 = {
      key: dish[1],
      titleEn: dish[1],
      titleSv: sv ? sv[0] : dish[1],
      price: dish[3]
    };
  }
  updateSelectedDishUIV29();
}

function selectedDishLabelV29(){
  if(!selectedDishV29) return "";
  const lang = (typeof currentLanguage!=="undefined" ? currentLanguage : "sv");
  const title = lang==="sv" ? selectedDishV29.titleSv : selectedDishV29.titleEn;
  return `${title} – ${selectedDishV29.price}`;
}

function updateSelectedDishUIV29(){
  const box = document.getElementById("selectedDishBox");
  const text = document.getElementById("selectedDishText");
  const reviewRow = document.getElementById("reviewSelectedDishRow");
  const reviewText = document.getElementById("reviewSelectedDish");

  if(selectedDishV29){
    const label = selectedDishLabelV29();
    if(box) box.hidden = false;
    if(text) text.textContent = label;
    if(reviewRow) reviewRow.hidden = false;
    if(reviewText) reviewText.textContent = label;
  }else{
    if(box) box.hidden = true;
    if(text) text.textContent = "";
    if(reviewRow) reviewRow.hidden = true;
    if(reviewText) reviewText.textContent = "";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const clearBtn = document.getElementById("clearSelectedDish");
  if(clearBtn){
    clearBtn.addEventListener("click", () => setSelectedDishV29(null));
  }

  // Keep selected dish text synchronized when language changes.
  document.querySelectorAll("[data-lang]").forEach(btn => {
    btn.addEventListener("click", () => setTimeout(updateSelectedDishUIV29, 0));
  });
});


function selectedDishLineV29(){
  if(!selectedDishV29) return "";
  const lang = (typeof currentLanguage!=="undefined" ? currentLanguage : "sv");
  return `${lang==="sv" ? "Vald rätt" : "Selected dish"}: ${selectedDishLabelV29()}`;
}

document.addEventListener("DOMContentLoaded", () => {
  const reservationFormV29 = document.querySelector("#reservation form") || document.querySelector("form");
  if(reservationFormV29){
    reservationFormV29.addEventListener("submit", () => {
      setTimeout(() => {
        updateSelectedDishUIV29(); // review sync
      }, 0);
    });
  }
});


/* ===== Backend V1: real reservation storage ===== */
(function(){
  "use strict";

  function backendLang(){
    const s=(localStorage.getItem("testRestaurantLanguageV12") ||
             localStorage.getItem("testRestaurantLanguage") ||
             document.documentElement.lang || "sv").toLowerCase();
    return s.startsWith("en") ? "en" : "sv";
  }

  function byId(id){ return document.getElementById(id); }

  function currentReference(){
    const ready=byId("readyRefValue");
    if(ready && ready.textContent && ready.textContent.trim() !== "—") return ready.textContent.trim();

    const refBox=byId("reservationReference");
    if(refBox && refBox.textContent){
      const m=refBox.textContent.match(/TR-\d{6}-\d{4}/);
      if(m) return m[0];
    }

    if(typeof window.v14ReservationReference==="function"){
      try{return window.v14ReservationReference();}catch(e){}
    }
    return "";
  }

  function selectedDishPayload(){
    try{
      if(typeof selectedDishV29!=="undefined" && selectedDishV29){
        return {
          name_sv:selectedDishV29.titleSv || selectedDishV29.key || "",
          name_en:selectedDishV29.titleEn || selectedDishV29.key || "",
          price:selectedDishV29.price || ""
        };
      }
    }catch(e){}
    return null;
  }

  function reservationPayload(){
    const dish=selectedDishPayload();
    return {
      reference: currentReference(),
      name: (byId("guestName")?.value || "").trim(),
      phone: (byId("guestPhone")?.value || "").trim(),
      email: (byId("guestEmail")?.value || "").trim(),
      guests: Number(byId("guestCount")?.value || 0),
      reservation_date: byId("reservationDate")?.value || "",
      reservation_time: byId("reservationTime")?.value || "",
      special_requests: (byId("specialRequests")?.value || "").trim(),
      selected_dish_name_sv: dish?.name_sv || "",
      selected_dish_name_en: dish?.name_en || "",
      selected_dish_price: dish?.price || "",
      language: backendLang()
    };
  }

  function setMessage(text, kind){
    const el=byId("backendReservationMessage");
    if(!el)return;
    el.textContent=text;
    el.className="backend-message " + (kind || "");
    el.hidden=false;
  }

  async function saveReservation(){
    const btn=byId("saveReservationBackend");
    if(!btn)return;

    const sv=backendLang()==="sv";
    btn.disabled=true;
    btn.textContent=sv ? "Sparar…" : "Saving…";
    setMessage(sv ? "Skickar bokningen till restaurangens server…" : "Sending the reservation to the restaurant server…","info");

    try{
      const response=await fetch("/api/reservations",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(reservationPayload())
      });

      const data=await response.json().catch(()=>({}));

      if(response.ok){
        setMessage(
          sv
            ? `Bokningen är sparad. Referens: ${data.reference}. Status: Väntar på bekräftelse.`
            : `Reservation saved. Reference: ${data.reference}. Status: Pending confirmation.`,
          "success"
        );
        btn.textContent=sv ? "Bokning sparad ✓" : "Reservation saved ✓";
        btn.disabled=true;
        document.dispatchEvent(new CustomEvent("reservation:backend-saved",{detail:data}));
      }else if(response.status===409 && (data.code==="duplicate_reservation" || data.reference)){
        setMessage(
          sv
            ? "Den här bokningen verkar redan vara sparad för samma e-post, datum och tid."
            : "This reservation appears to have already been saved for the same email, date and time.",
          "warning"
        );
        btn.disabled=false;
        btn.textContent=sv ? "Spara bokning" : "Save reservation";
      }else if(response.status===409 && data.code==="slot_capacity"){
        const remaining=Number(data.remaining_capacity || 0);
        setMessage(
          sv
            ? `Tiden har inte längre tillräckligt med plats. ${remaining} platser återstår. Välj en annan tid.`
            : `This time no longer has enough capacity. ${remaining} seats remain. Please choose another time.`,
          "warning"
        );
        btn.disabled=false;
        btn.textContent=sv ? "Välj annan tid" : "Choose another time";
        document.dispatchEvent(new CustomEvent("reservation:capacity-changed"));
      }else{
        const msg=data.error || (sv ? "Bokningen kunde inte sparas." : "The reservation could not be saved.");
        setMessage(msg,"error");
        btn.disabled=false;
        btn.textContent=sv ? "Försök igen" : "Try again";
      }
    }catch(err){
      setMessage(
        sv
          ? "Kan inte nå backend-servern. Kontrollera att Flask körs i terminalen."
          : "Cannot reach the backend server. Make sure Flask is running in the terminal.",
        "error"
      );
      btn.disabled=false;
      btn.textContent=sv ? "Försök igen" : "Try again";
    }
  }

  document.addEventListener("DOMContentLoaded",function(){
    const btn=byId("saveReservationBackend");
    if(btn){
      btn.textContent=backendLang()==="sv" ? "Spara bokning" : "Save reservation";
      btn.addEventListener("click",saveReservation);
    }

    document.querySelectorAll("[data-lang]").forEach(function(langBtn){
      langBtn.addEventListener("click",function(){
        setTimeout(function(){
          const b=byId("saveReservationBackend");
          if(b && !b.disabled){
            b.textContent=backendLang()==="sv" ? "Spara bokning" : "Save reservation";
          }
        },30);
      });
    });

    const newBtn=byId("newReservation");
    if(newBtn){
      newBtn.addEventListener("click",function(){
        const b=byId("saveReservationBackend");
        if(b){
          b.disabled=false;
          b.textContent=backendLang()==="sv" ? "Spara bokning" : "Save reservation";
        }
        const msg=byId("backendReservationMessage");
        if(msg) msg.hidden=true;
      });
    }
  });
})();


/* ===== Backend V6: live capacity-aware reservation times ===== */
(function(){
  "use strict";

  let availabilityRequestId=0;
  let cachedDate="";
  let cachedSlots=[];

  function byId(id){ return document.getElementById(id); }

  function lang(){
    const s=(localStorage.getItem("testRestaurantLanguageV12") ||
             localStorage.getItem("testRestaurantLanguage") ||
             document.documentElement.lang || "sv").toLowerCase();
    return s.startsWith("en") ? "en" : "sv";
  }

  function guestCount(){
    const value=Number(byId("guestCount")?.value || 0);
    return Number.isFinite(value) && value > 0 ? value : 1;
  }

  function hint(text,kind){
    const el=byId("timeAvailabilityHint");
    if(!el) return;
    el.textContent=text;
    el.classList.remove("capacity-ok","capacity-warning","capacity-error");
    if(kind) el.classList.add(kind);
  }

  function applyAvailability(slots){
    const select=byId("reservationTime");
    if(!select) return;

    const needed=guestCount();
    let suitable=0;
    let full=0;
    let low=0;
    const map=new Map(slots.map(slot=>[slot.time,slot]));

    [...select.options].forEach(option=>{
      if(!option.value) return;
      const slot=map.get(option.value);
      if(!slot){
        option.disabled=true;
        return;
      }

      const remaining=Number(slot.remaining_capacity || 0);
      const enough=remaining >= needed;
      option.disabled=!enough;

      if(remaining===0){
        full++;
        option.textContent=lang()==="en"
          ? `${slot.time} — Full`
          : `${slot.time} — Fullbokat`;
      }else if(!enough){
        option.textContent=lang()==="en"
          ? `${slot.time} — ${remaining} left (not enough for ${needed})`
          : `${slot.time} — ${remaining} kvar (inte nog för ${needed})`;
      }else{
        suitable++;
        if(remaining<=4) low++;
        option.textContent=lang()==="en"
          ? `${slot.time} — ${remaining} seats left`
          : `${slot.time} — ${remaining} platser kvar`;
      }
    });

    if(select.value){
      const selected=select.options[select.selectedIndex];
      if(selected && selected.disabled) select.value="";
    }

    if(suitable===0){
      hint(
        lang()==="en"
          ? `No time has enough capacity for ${needed} guest${needed===1?"":"s"}. Please choose another date or party size.`
          : `Ingen tid har tillräcklig kapacitet för ${needed} gäst${needed===1?"":"er"}. Välj ett annat datum eller antal gäster.`,
        "capacity-error"
      );
    }else if(low>0 || full>0){
      hint(
        lang()==="en"
          ? `${suitable} suitable time${suitable===1?"":"s"}. Full or insufficient slots are disabled.`
          : `${suitable} lämplig${suitable===1?"":"a"} tid${suitable===1?"":"er"}. Fullbokade eller otillräckliga tider är inaktiverade.`,
        "capacity-warning"
      );
    }else{
      hint(
        lang()==="en"
          ? `${suitable} available time${suitable===1?"":"s"} for your party.`
          : `${suitable} tillgänglig${suitable===1?"":"a"} tid${suitable===1?"":"er"} för ert sällskap.`,
        "capacity-ok"
      );
    }
  }

  async function refreshCapacity(){
    const date=byId("reservationDate")?.value || "";
    const select=byId("reservationTime");
    if(!select || !date) return;

    // If only the party size changed, re-apply already fetched values instantly.
    if(date===cachedDate && cachedSlots.length){
      applyAvailability(cachedSlots);
      return;
    }

    const requestId=++availabilityRequestId;
    hint(lang()==="en" ? "Checking live availability…" : "Kontrollerar lediga tider…","");

    try{
      const response=await fetch(`/api/availability?date=${encodeURIComponent(date)}`,{cache:"no-store"});
      const data=await response.json().catch(()=>({}));
      if(requestId!==availabilityRequestId) return;

      if(!response.ok || !data.ok){
        hint(lang()==="en" ? "Could not load live availability." : "Kunde inte hämta aktuell tillgänglighet.","capacity-error");
        return;
      }

      cachedDate=date;
      cachedSlots=Array.isArray(data.slots) ? data.slots : [];

      if(data.closed || cachedSlots.length===0){
        hint(lang()==="en" ? "The restaurant is closed on this date." : "Restaurangen är stängd detta datum.","capacity-error");
        return;
      }

      applyAvailability(cachedSlots);
    }catch(err){
      if(requestId!==availabilityRequestId) return;
      hint(
        lang()==="en"
          ? "Live capacity is temporarily unavailable. The server will still validate the booking when you save it."
          : "Aktuell kapacitet kunde inte hämtas. Servern kontrollerar ändå bokningen när du sparar den.",
        "capacity-warning"
      );
    }
  }

  function scheduleRefresh(forceFetch){
    if(forceFetch){ cachedDate=""; cachedSlots=[]; }
    // V21 rebuilds the time <select> on date/language changes; run after it.
    setTimeout(refreshCapacity,40);
  }

  document.addEventListener("DOMContentLoaded",function(){ scheduleRefresh(true); });

  document.addEventListener("change",function(e){
    if(e.target?.id==="reservationDate") scheduleRefresh(true);
    if(e.target?.id==="guestCount") scheduleRefresh(false);
  });

  document.addEventListener("click",function(e){
    if(e.target?.closest("[data-v12-lang],[data-lang]")) scheduleRefresh(false);
  });

  // Refresh after the backend confirms a save, or rejects a slot because
  // another booking consumed the remaining capacity.
  document.addEventListener("reservation:backend-saved",function(){ scheduleRefresh(true); });
  document.addEventListener("reservation:capacity-changed",function(){ scheduleRefresh(true); });

  window.v6RefreshCapacity=refreshCapacity;
})();
