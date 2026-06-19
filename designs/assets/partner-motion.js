/* ─────────────────────────────────────────────────────────────
   Partner Motion — shared motion engine for the Headout Here
   partner journey. No dependencies. Honors prefers-reduced-motion.

   Exposes window.PF:
     PF.reduced                          → boolean
     PF.reveal(root?)                    → observe [data-reveal] in root
     PF.countUp(el, to, opts)            → animate a number
     PF.autoCount(root?)                 → run [data-countup] in root
     PF.pageTransition(opts)             → body fade in/out on same-flow nav
     PF.confetti(opts)                   → one-shot confetti burst
     PF.ping({title,sub,amount,icon})    → top-right "just landed" toast
     PF.rail(steps, activeIndex, mount)  → render journey progress rail
   ───────────────────────────────────────────────────────────── */
(function(){
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── reveal on scroll ── */
  let io;
  function reveal(root){
    const els = (root||document).querySelectorAll('[data-reveal]:not(.is-in)');
    if(reduced){ els.forEach(el=>el.classList.add('is-in')); return; }
    if(!io){
      io = new IntersectionObserver((entries)=>{
        entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); } });
      },{threshold:.14, rootMargin:'0px 0px -8% 0px'});
    }
    els.forEach(el=>io.observe(el));
  }

  /* ── count-up ── */
  const easeOut = t => 1 - Math.pow(1 - t, 3);
  function countUp(el, to, opts){
    opts = opts || {};
    const prefix = opts.prefix||'', suffix = opts.suffix||'';
    const decimals = opts.decimals!=null ? opts.decimals : (String(to).includes('.')?2:0);
    const dur = opts.duration!=null ? opts.duration : 1100;
    const fmt = v => prefix + (opts.group!==false ? Number(v.toFixed(decimals)).toLocaleString(undefined,{minimumFractionDigits:decimals,maximumFractionDigits:decimals}) : v.toFixed(decimals)) + suffix;
    if(reduced || dur<=0){ el.textContent = fmt(to); return; }
    const from = opts.from!=null ? opts.from : 0;
    el.classList.add('pf-counting');
    const t0 = performance.now();
    (function frame(now){
      const p = Math.min(1,(now-t0)/dur);
      el.textContent = fmt(from + (to-from)*easeOut(p));
      if(p<1) requestAnimationFrame(frame);
      else { el.textContent = fmt(to); setTimeout(()=>el.classList.remove('pf-counting'),120); }
    })(t0);
  }
  // parse "€1,248.50" → {prefix:'€', value:1248.5, decimals:2}
  function parseNum(str){
    const s = String(str).trim();
    const m = s.match(/-?[\d.,]+/);
    if(!m) return null;
    const raw = m[0];
    const prefix = s.slice(0, m.index);
    const suffix = s.slice(m.index + raw.length);
    const value = parseFloat(raw.replace(/,/g,''));
    const dec = (raw.split('.')[1]||'').length;
    return isNaN(value) ? null : {prefix, suffix, value, decimals:dec};
  }
  function autoCount(root){
    (root||document).querySelectorAll('[data-countup]:not([data-counted])').forEach(el=>{
      const target = el.getAttribute('data-countup') || el.textContent;
      const p = parseNum(target);
      if(!p){ return; }
      el.setAttribute('data-counted','1');
      countUp(el, p.value, {prefix:p.prefix, suffix:p.suffix, decimals:p.decimals,
        duration: +el.getAttribute('data-countup-dur') || 1100});
    });
  }

  /* ── page transition ── */
  function pageTransition(opts){
    opts = opts||{};
    const sel = opts.selector || 'a[href$=".html"], a[data-flow]';
    document.body.classList.add('pf-fade');
    requestAnimationFrame(()=>document.body.classList.add('is-ready'));
    if(reduced) return;
    document.addEventListener('click', e=>{
      const a = e.target.closest(sel);
      if(!a) return;
      const href = a.getAttribute('href');
      if(!href || href.startsWith('#') || a.target==='_blank' || a.hasAttribute('data-no-fade')) return;
      if(a.getAttribute('aria-disabled')==='true'){ return; }
      if(e.metaKey||e.ctrlKey||e.shiftKey) return;
      e.preventDefault();
      document.body.classList.add('is-leaving');
      setTimeout(()=>{ window.location.href = href; }, 240);
    });
  }

  /* ── confetti ── */
  function confetti(opts){
    if(reduced) return;
    opts = opts||{};
    const n = opts.count||90;
    const colors = opts.colors || ['#8000ff','#ff007a','#15d676','#ffbc00','#cc99ff','#00c4eb'];
    const wrap = document.createElement('div');
    wrap.className='pf-confetti';
    let html='';
    for(let i=0;i<n;i++){
      const left = Math.random()*100;
      const dur = (1.8+Math.random()*1.8).toFixed(2);
      const delay = (Math.random()*.35).toFixed(2);
      const rot = (360+Math.random()*720).toFixed(0);
      const c = colors[i%colors.length];
      const w = (6+Math.random()*6).toFixed(0);
      html += `<i style="left:${left}%;background:${c};width:${w}px;--cf-dur:${dur}s;--cf-delay:${delay}s;--cf-rot:${rot}deg"></i>`;
    }
    wrap.innerHTML=html;
    document.body.appendChild(wrap);
    setTimeout(()=>wrap.remove(), (opts.life||3400));
  }

  /* ── live "just landed" ping ── */
  const CHECK = '<svg class="ee-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
  function ping(o){
    o = o||{};
    const el = document.createElement('div');
    el.className='pf-ping';
    el.innerHTML = `<span class="ic">${o.icon||CHECK}</span>
      <span class="tx"><b>${o.title||'Booking confirmed'}</b><span>${o.sub||''}</span></span>
      ${o.amount?`<span class="amt">${o.amount}</span>`:''}`;
    document.body.appendChild(el);
    requestAnimationFrame(()=>requestAnimationFrame(()=>el.classList.add('is-in')));
    setTimeout(()=>{ el.classList.remove('is-in'); setTimeout(()=>el.remove(),460); }, o.life||3200);
  }

  /* ── journey progress rail ── */
  function rail(steps, activeIndex, mount){
    const host = typeof mount==='string' ? document.querySelector(mount) : mount;
    if(!host) return;
    let html='';
    steps.forEach((label,i)=>{
      const state = i<activeIndex ? 'done' : (i===activeIndex ? 'active' : '');
      html += `<div class="seg ${i<activeIndex?'done':''}"><div class="node ${state}"><span class="dot"></span><span class="lbl">${label}</span></div>`;
      if(i<steps.length-1) html += `<span class="bar"></span>`;
      html += `</div>`;
    });
    host.className='pf-rail';
    host.innerHTML=html;
  }

  window.PF = { reduced, reveal, countUp, autoCount, parseNum, pageTransition, confetti, ping, rail };

  document.addEventListener('DOMContentLoaded', ()=>{
    reveal();
    if(!document.body.hasAttribute('data-no-autocount')) autoCount();
  });
})();
