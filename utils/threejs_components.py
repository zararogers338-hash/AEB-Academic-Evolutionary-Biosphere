# -*- coding: utf-8 -*-
"""AEB Three.js 可视化组件 v3 / Three.js Visualization Components v3
全面增强: 后期处理光效、粒子系统、标签系统、更好的交互、暂停控制
"""

import json
import streamlit as st
import streamlit.components.v1 as components

THREEJS_CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"


def _wrap_html(body_js: str, width: int = 800, height: int = 600, extra_head: str = "", show_pause: bool = False) -> str:
    pause_btn_css = ""
    pause_btn_html = ""
    if show_pause:
        pause_btn_css = """
#pause-btn{position:absolute;top:10px;right:12px;z-index:20;background:rgba(6,13,31,0.85);
  color:#00ffaa;border:1px solid rgba(0,255,170,0.4);border-radius:6px;padding:5px 14px;
  font-size:12px;cursor:pointer;backdrop-filter:blur(6px);font-family:'Segoe UI',system-ui,sans-serif;
  transition:all 0.2s;}
#pause-btn:hover{border-color:#00ffaa;background:rgba(0,255,170,0.15);}
"""
        pause_btn_html = '<button id="pause-btn" onclick="togglePause()">⏸ Pause</button>'

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body{{margin:0;overflow:hidden;background:#060d1f;font-family:'Segoe UI',system-ui,sans-serif;}}
canvas{{display:block;}}
#info{{position:absolute;top:10px;left:12px;color:rgba(0,255,170,0.7);font-size:11px;z-index:10;pointer-events:none;letter-spacing:0.5px;}}
#tooltip{{position:absolute;display:none;background:rgba(6,13,31,0.95);color:#00ffaa;padding:10px 14px;
  border:1px solid rgba(0,255,170,0.4);border-radius:8px;font-size:12px;z-index:20;pointer-events:none;
  max-width:320px;backdrop-filter:blur(8px);box-shadow:0 4px 20px rgba(0,255,136,0.15);line-height:1.5;}}
#tooltip b{{color:#00ffdd;font-size:13px;}}
#tooltip .tag{{display:inline-block;background:rgba(0,255,170,0.15);border:1px solid rgba(0,255,170,0.3);
  border-radius:4px;padding:1px 6px;margin:2px;font-size:10px;}}
.node-label{{position:absolute;color:#00ffaa;font-size:9px;pointer-events:none;
  text-shadow:0 0 4px rgba(0,255,136,0.6), 0 1px 2px rgba(0,0,0,0.8);
  transform:translate(-50%,-100%);white-space:nowrap;z-index:5;opacity:0.92;
  font-family:'Segoe UI',system-ui,sans-serif;letter-spacing:0.3px;}}
{pause_btn_css}
</style>
<script src="{THREEJS_CDN}"></script>
{extra_head}
</head><body>
<div id="info"></div>
<div id="tooltip"></div>
<div id="labels"></div>
{pause_btn_html}
<script>
{body_js}
</script></body></html>"""


def render_force_graph(nodes: list, edges: list, width: int = 800, height: int = 600, show_labels: bool = False):
    """Render an enhanced force-directed graph with glow effects and label system."""
    js = f"""
const DATA = {{nodes: {json.dumps(nodes, ensure_ascii=False)}, edges: {json.dumps(edges, ensure_ascii=False)}}};
const W = {width}, H = {height};
const SHOW_LABELS = {'true' if show_labels else 'false'};
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x060d1f, 0.003);
const camera = new THREE.PerspectiveCamera(55, W/H, 0.1, 3000);
camera.position.set(0, 0, 350);
const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
renderer.setSize(W, H); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x060d1f);
document.body.appendChild(renderer.domElement);

const nodeMap = {{}}, nodeMeshes = [], edgeLines = [], glowMeshes = [];

// Lights
scene.add(new THREE.AmbientLight(0x223344, 0.6));
const p1 = new THREE.PointLight(0x00ffaa, 1.2, 600); p1.position.set(150, 120, 150); scene.add(p1);
const p2 = new THREE.PointLight(0x0066ff, 0.6, 400); p2.position.set(-100, -80, 100); scene.add(p2);

// Label system
const labelsContainer = document.getElementById('labels');
const labelElements = [];

// Create nodes with glow
DATA.nodes.forEach((n, idx) => {{
    const baseSize = Math.max(1.5, Math.sqrt(n.size) * 5);
    const col = new THREE.Color(n.color || '#00ff88');
    const geo = new THREE.SphereGeometry(baseSize, 20, 20);
    const mat = new THREE.MeshPhongMaterial({{color:col, emissive:col.clone().multiplyScalar(0.4), transparent:true, opacity:0.9, shininess:80}});
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set((Math.random()-0.5)*250, (Math.random()-0.5)*250, (Math.random()-0.5)*120);
    mesh.userData = n;
    scene.add(mesh);
    nodeMap[n.id] = mesh;
    nodeMeshes.push(mesh);
    // Glow outer
    const gGeo = new THREE.SphereGeometry(baseSize * 1.6, 12, 12);
    const gMat = new THREE.MeshBasicMaterial({{color:col, transparent:true, opacity:0.08}});
    const glow = new THREE.Mesh(gGeo, gMat);
    mesh.add(glow);
    glowMeshes.push(glow);
    // Label element
    if(SHOW_LABELS) {{
        const lbl = document.createElement('div');
        lbl.className = 'node-label';
        lbl.textContent = n.label || n.id;
        lbl.style.color = n.color || '#00ffaa';
        labelsContainer.appendChild(lbl);
        labelElements.push({{el: lbl, mesh: mesh}});
    }}
}});

// Create edges with gradient
DATA.edges.forEach(e => {{
    const alpha = Math.min(0.7, e.weight / 8 + 0.08);
    const mat = new THREE.LineBasicMaterial({{color:0x00ff88, transparent:true, opacity:alpha, linewidth:1}});
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(6);
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const line = new THREE.Line(geo, mat);
    line.userData = {{source: e.source, target: e.target, weight: e.weight}};
    scene.add(line); edgeLines.push(line);
}});

// Background particles
const pGeo = new THREE.BufferGeometry();
const pCount = 300;
const pPos = new Float32Array(pCount * 3);
for(let i=0; i<pCount*3; i++) pPos[i] = (Math.random()-0.5)*800;
pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
const pMat = new THREE.PointsMaterial({{color:0x00ff88, size:0.8, transparent:true, opacity:0.3}});
scene.add(new THREE.Points(pGeo, pMat));

// Force simulation
function simStep() {{
    const ns = nodeMeshes;
    for(let i=0; i<ns.length; i++) {{
        for(let j=i+1; j<ns.length; j++) {{
            const dx = ns[j].position.x - ns[i].position.x;
            const dy = ns[j].position.y - ns[i].position.y;
            const dz = ns[j].position.z - ns[i].position.z;
            const dist = Math.max(1, Math.sqrt(dx*dx+dy*dy+dz*dz));
            const rep = 60 / (dist*dist);
            ns[i].position.x -= dx*rep; ns[i].position.y -= dy*rep;
            ns[j].position.x += dx*rep; ns[j].position.y += dy*rep;
        }}
    }}
    edgeLines.forEach(l => {{
        const s = nodeMap[l.userData.source], t = nodeMap[l.userData.target];
        if(s && t) {{
            const dx = t.position.x-s.position.x, dy = t.position.y-s.position.y, dz = t.position.z-s.position.z;
            const dist = Math.sqrt(dx*dx+dy*dy+dz*dz);
            const attr = (dist - 50) * 0.004;
            s.position.x += dx*attr; s.position.y += dy*attr;
            t.position.x -= dx*attr; t.position.y -= dy*attr;
            const p = l.geometry.attributes.position.array;
            p[0]=s.position.x;p[1]=s.position.y;p[2]=s.position.z;
            p[3]=t.position.x;p[4]=t.position.y;p[5]=t.position.z;
            l.geometry.attributes.position.needsUpdate = true;
        }}
    }});
}}

// Update label positions
function updateLabels() {{
    labelElements.forEach(item => {{
        const pos = item.mesh.position.clone();
        pos.project(camera);
        const x = (pos.x * 0.5 + 0.5) * W;
        const y = (-pos.y * 0.5 + 0.5) * H;
        if(pos.z < 1) {{
            item.el.style.display = 'block';
            item.el.style.left = x + 'px';
            item.el.style.top = (y - 8) + 'px';
        }} else {{
            item.el.style.display = 'none';
        }}
    }});
}}

// Interaction
const rc = new THREE.Raycaster(), mouse = new THREE.Vector2();
let selNode = null;
const tooltip = document.getElementById('tooltip');

renderer.domElement.addEventListener('mousemove', (e) => {{
    mouse.x = (e.offsetX/W)*2-1; mouse.y = -(e.offsetY/H)*2+1;
    rc.setFromCamera(mouse, camera);
    const hits = rc.intersectObjects(nodeMeshes);
    if(hits.length) {{
        const nd = hits[0].object.userData;
        tooltip.style.display='block'; tooltip.style.left=(e.offsetX+18)+'px'; tooltip.style.top=(e.offsetY+18)+'px';
        tooltip.innerHTML = '<b>'+nd.label+'</b><br><span class="tag">Score: '+(nd.size||0).toFixed(4)+'</span> <span class="tag">Group: '+(nd.group||0)+'</span>';
        document.body.style.cursor = 'pointer';
    }} else {{ tooltip.style.display='none'; document.body.style.cursor='default'; }}
}});

renderer.domElement.addEventListener('click', (e) => {{
    rc.setFromCamera(mouse, camera);
    const hits = rc.intersectObjects(nodeMeshes);
    if(hits.length) {{
        if(selNode) {{ selNode.material.emissive.copy(selNode.material.color).multiplyScalar(0.4); selNode.scale.set(1,1,1); }}
        selNode = hits[0].object;
        selNode.material.emissive.setHex(0x00ffff); selNode.scale.set(1.3,1.3,1.3);
        const nid = selNode.userData.id;
        edgeLines.forEach(l => {{
            const isConn = l.userData.source===nid || l.userData.target===nid;
            l.material.opacity = isConn ? 0.8 : 0.03;
            l.material.color.setHex(isConn ? 0x00ffdd : 0x00ff88);
        }});
    }}
}});

renderer.domElement.addEventListener('wheel', (e) => {{ camera.position.z += e.deltaY*0.4; camera.position.z=Math.max(60,Math.min(800,camera.position.z)); }});
let drag=false,px=0,py=0;
renderer.domElement.addEventListener('mousedown',(e)=>{{drag=true;px=e.clientX;py=e.clientY;}});
renderer.domElement.addEventListener('mouseup',()=>{{drag=false;}});
renderer.domElement.addEventListener('mousemove',(e)=>{{ if(drag){{scene.rotation.y+=(e.clientX-px)*0.004;scene.rotation.x+=(e.clientY-py)*0.004;px=e.clientX;py=e.clientY;}} }});

let frame=0;
function animate() {{
    requestAnimationFrame(animate);
    if(frame<250) simStep();
    frame++;
    const t = Date.now() * 0.001;
    glowMeshes.forEach((g,i) => {{ g.material.opacity = 0.06 + Math.sin(t*2+i)*0.03; }});
    if(SHOW_LABELS) updateLabels();
    renderer.render(scene, camera);
}}
document.getElementById('info').innerHTML = 'Nodes: '+DATA.nodes.length+' | Edges: '+DATA.edges.length+' | Scroll zoom · Drag rotate · Click select';
animate();
"""
    html = _wrap_html(js, width, height)
    components.html(html, width=width, height=height + 10, scrolling=False)


def render_evolution_tree(tree_data: dict, width: int = 800, height: int = 600, show_labels: bool = False):
    """Render enhanced 3D evolution tree with flowing branch animation."""
    js = f"""
const TREE = {json.dumps(tree_data, ensure_ascii=False)};
const W={width}, H={height};
const SHOW_LABELS = {'true' if show_labels else 'false'};
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x060d1f, 0.0025);
const camera = new THREE.PerspectiveCamera(55, W/H, 0.1, 2000);
camera.position.set(0, 30, 350);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W, H); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x060d1f);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0x334455, 0.7));
const l1 = new THREE.PointLight(0x00ffaa, 1.2, 600); l1.position.set(100, 150, 100); scene.add(l1);
const l2 = new THREE.PointLight(0x4444ff, 0.5, 400); l2.position.set(-80, -50, 80); scene.add(l2);

const tooltip = document.getElementById('tooltip');
const allMeshes = [], branchLines = [];
const labelsContainer = document.getElementById('labels');
const labelElements = [];

function buildTree(node, x, y, z, depth, spread) {{
    const size = Math.max(2, (node.score || 0.01) * 25);
    const hue = 0.45 - depth * 0.08;
    const color = new THREE.Color().setHSL(Math.max(0, hue), 0.85, 0.55);
    const geo = new THREE.SphereGeometry(size, 16, 16);
    const mat = new THREE.MeshPhongMaterial({{color, emissive:color.clone().multiplyScalar(0.35), transparent:true, opacity:0.92, shininess:60}});
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, y, z);
    mesh.userData = {{name: node.name, score: node.score, year: node.year, depth}};
    scene.add(mesh); allMeshes.push(mesh);
    // Glow
    const gg = new THREE.SphereGeometry(size*1.8, 8, 8);
    const gm = new THREE.MeshBasicMaterial({{color, transparent:true, opacity:0.06}});
    mesh.add(new THREE.Mesh(gg, gm));
    // Label
    if(SHOW_LABELS) {{
        const lbl = document.createElement('div');
        lbl.className = 'node-label';
        lbl.textContent = node.name || '';
        lbl.style.color = '#' + color.getHexString();
        labelsContainer.appendChild(lbl);
        labelElements.push({{el: lbl, mesh: mesh}});
    }}

    if(node.children) {{
        const n = node.children.length;
        node.children.forEach((child, i) => {{
            const angle = (i / Math.max(1,n)) * Math.PI * 2;
            const cx = x + Math.cos(angle) * spread;
            const cy = y - 45;
            const cz = z + Math.sin(angle) * spread;
            const mid = new THREE.Vector3((x+cx)/2, (y+cy)/2+10, (z+cz)/2);
            const curve = new THREE.QuadraticBezierCurve3(
                new THREE.Vector3(x,y,z), mid, new THREE.Vector3(cx,cy,cz));
            const pts = curve.getPoints(20);
            const branchColor = color.clone().lerp(new THREE.Color(0x00ff88), 0.3);
            const lmat = new THREE.LineBasicMaterial({{color: branchColor, transparent:true, opacity:0.45}});
            const lgeo = new THREE.BufferGeometry().setFromPoints(pts);
            const line = new THREE.Line(lgeo, lmat);
            scene.add(line); branchLines.push(line);
            buildTree(child, cx, cy, cz, depth+1, spread*0.55);
        }});
    }}
}}
buildTree(TREE, 0, 120, 0, 0, 90);

// Background particles
const bg = new THREE.BufferGeometry(); const bc = 200;
const bp = new Float32Array(bc*3);
for(let i=0;i<bc*3;i++) bp[i]=(Math.random()-0.5)*700;
bg.setAttribute('position', new THREE.BufferAttribute(bp,3));
scene.add(new THREE.Points(bg, new THREE.PointsMaterial({{color:0x00ffaa, size:0.6, transparent:true, opacity:0.2}})));

function updateLabels() {{
    labelElements.forEach(item => {{
        const pos = item.mesh.position.clone();
        pos.project(camera);
        const x = (pos.x * 0.5 + 0.5) * W;
        const y = (-pos.y * 0.5 + 0.5) * H;
        if(pos.z < 1) {{
            item.el.style.display = 'block';
            item.el.style.left = x + 'px';
            item.el.style.top = (y - 8) + 'px';
        }} else {{
            item.el.style.display = 'none';
        }}
    }});
}}

// Interaction
const rc = new THREE.Raycaster();
renderer.domElement.addEventListener('mousemove', (e) => {{
    const m = new THREE.Vector2((e.offsetX/W)*2-1, -(e.offsetY/H)*2+1);
    rc.setFromCamera(m, camera);
    const h = rc.intersectObjects(allMeshes);
    if(h.length) {{
        const d=h[0].object.userData;
        tooltip.style.display='block'; tooltip.style.left=(e.offsetX+15)+'px'; tooltip.style.top=(e.offsetY+15)+'px';
        tooltip.innerHTML='<b>'+d.name+'</b><br><span class="tag">Score: '+(d.score||0).toFixed(4)+'</span> <span class="tag">Depth: '+d.depth+'</span><br><span class="tag">Year: '+(d.year||'?')+'</span>';
    }} else tooltip.style.display='none';
}});

let drag=false,px=0,py=0;
renderer.domElement.addEventListener('mousedown',(e)=>{{drag=true;px=e.clientX;py=e.clientY;}});
renderer.domElement.addEventListener('mouseup',()=>{{drag=false;}});
renderer.domElement.addEventListener('mousemove',(e)=>{{if(drag){{scene.rotation.y+=(e.clientX-px)*0.004;scene.rotation.x+=(e.clientY-py)*0.004;px=e.clientX;py=e.clientY;}}  }});
renderer.domElement.addEventListener('wheel',(e)=>{{camera.position.z+=e.deltaY*0.4;camera.position.z=Math.max(80,Math.min(800,camera.position.z));}});

document.getElementById('info').innerHTML = 'Evolution Tree — Scroll zoom · Drag rotate · Hover for details';
function animate() {{
    requestAnimationFrame(animate);
    const t = Date.now()*0.0008;
    l1.position.x = Math.sin(t)*120; l1.position.z = Math.cos(t)*120;
    if(SHOW_LABELS) updateLabels();
    renderer.render(scene, camera);
}}
animate();
"""
    html = _wrap_html(js, width, height)
    components.html(html, width=width, height=height + 10, scrolling=False)


def render_fossil_layers(layers: list, width: int = 800, height: int = 600, show_labels: bool = False):
    """Render geological fossil layers with depth-of-field feel."""
    js = f"""
const LAYERS = {json.dumps(layers, ensure_ascii=False)};
const W={width}, H={height};
const SHOW_LABELS = {'true' if show_labels else 'false'};
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x1a0e00, 200, 700);
const camera = new THREE.PerspectiveCamera(50, W/H, 0.1, 2000);
camera.position.set(0, 0, 400);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W, H); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x1a0e00);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0x665544, 0.7));
const dl = new THREE.DirectionalLight(0xffeedd, 0.8); dl.position.set(60, 120, 100); scene.add(dl);
const sl = new THREE.PointLight(0xff8844, 0.4, 300); sl.position.set(0, 60, 150); scene.add(sl);

const tooltip = document.getElementById('tooltip');
const allMeshes = [];
const labelsContainer = document.getElementById('labels');
const labelElements = [];

LAYERS.forEach((layer, i) => {{
    const y = 120 - i * 45;
    const col = new THREE.Color(layer.color || '#886644');
    const geo = new THREE.BoxGeometry(220, 32, 110, 2, 2, 2);
    const mat = new THREE.MeshPhongMaterial({{color: col, transparent:true, opacity:0.55, side:THREE.DoubleSide}});
    const slab = new THREE.Mesh(geo, mat);
    slab.position.set(0, y, 0);
    slab.userData = {{type:'layer', year_range: layer.year_range, keywords: layer.keywords, index: i}};
    scene.add(slab); allMeshes.push(slab);
    // Layer label
    if(SHOW_LABELS) {{
        const lbl = document.createElement('div');
        lbl.className = 'node-label';
        lbl.textContent = layer.year_range;
        lbl.style.color = '#ccaa66';
        lbl.style.fontSize = '10px';
        lbl.style.fontWeight = 'bold';
        labelsContainer.appendChild(lbl);
        labelElements.push({{el: lbl, mesh: slab}});
    }}
    // Side label line
    const lp = [new THREE.Vector3(115, y, 0), new THREE.Vector3(130, y, 0)];
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(lp), new THREE.LineBasicMaterial({{color:0xaa8866, opacity:0.5, transparent:true}})));
    // Fossils
    (layer.keywords || []).forEach((kw, j) => {{
        const fx = (Math.random()-0.5)*180, fy = y + (Math.random()-0.5)*22, fz = (Math.random()-0.5)*90;
        const age = i / Math.max(1, LAYERS.length-1);
        const fCol = new THREE.Color().setHSL(0.1 - age*0.05, 0.6 - age*0.3, 0.6 - age*0.2);
        const fg = new THREE.SphereGeometry(1.5+Math.random(), 8, 8);
        const fm = new THREE.MeshPhongMaterial({{color: fCol, emissive: fCol.clone().multiplyScalar(0.2), transparent:true, opacity:0.75}});
        const fossil = new THREE.Mesh(fg, fm);
        fossil.position.set(fx, fy, fz);
        fossil.userData = {{type:'fossil', name: kw, layer: layer.year_range}};
        scene.add(fossil); allMeshes.push(fossil);
        if(SHOW_LABELS) {{
            const lbl = document.createElement('div');
            lbl.className = 'node-label';
            lbl.textContent = kw;
            lbl.style.color = '#' + fCol.getHexString();
            lbl.style.fontSize = '8px';
            labelsContainer.appendChild(lbl);
            labelElements.push({{el: lbl, mesh: fossil}});
        }}
    }});
}});

// Floating dust
const dg = new THREE.BufferGeometry(); const dc = 150;
const dp = new Float32Array(dc*3);
for(let i=0;i<dc*3;i++) dp[i]=(Math.random()-0.5)*500;
dg.setAttribute('position', new THREE.BufferAttribute(dp,3));
const dust = new THREE.Points(dg, new THREE.PointsMaterial({{color:0xccaa66, size:0.8, transparent:true, opacity:0.25}}));
scene.add(dust);

function updateLabels() {{
    labelElements.forEach(item => {{
        const pos = item.mesh.position.clone();
        pos.project(camera);
        const x = (pos.x * 0.5 + 0.5) * W;
        const y = (-pos.y * 0.5 + 0.5) * H;
        if(pos.z < 1) {{
            item.el.style.display = 'block';
            item.el.style.left = x + 'px';
            item.el.style.top = (y - 8) + 'px';
        }} else {{
            item.el.style.display = 'none';
        }}
    }});
}}

renderer.domElement.addEventListener('mousemove', (e) => {{
    const m = new THREE.Vector2((e.offsetX/W)*2-1, -(e.offsetY/H)*2+1);
    const rc = new THREE.Raycaster(); rc.setFromCamera(m, camera);
    const h = rc.intersectObjects(allMeshes);
    if(h.length) {{
        const d = h[0].object.userData;
        tooltip.style.display='block'; tooltip.style.left=(e.offsetX+15)+'px'; tooltip.style.top=(e.offsetY+15)+'px';
        if(d.type==='layer') tooltip.innerHTML='<b>\U0001faa8 '+d.year_range+'</b><br>'+((d.keywords||[]).slice(0,8).map(k=>'<span class="tag">'+k+'</span>').join(' '));
        else tooltip.innerHTML='\U0001f9b4 <b>'+d.name+'</b><br><span class="tag">Layer: '+d.layer+'</span>';
    }} else tooltip.style.display='none';
}});

let drag=false,px=0,py=0;
renderer.domElement.addEventListener('mousedown',(e)=>{{drag=true;px=e.clientX;py=e.clientY;}});
renderer.domElement.addEventListener('mouseup',()=>{{drag=false;}});
renderer.domElement.addEventListener('mousemove',(e)=>{{if(drag){{scene.rotation.y+=(e.clientX-px)*0.004;scene.rotation.x+=(e.clientY-py)*0.004;px=e.clientX;py=e.clientY;}}}});
renderer.domElement.addEventListener('wheel',(e)=>{{camera.position.z+=e.deltaY*0.4;camera.position.z=Math.max(120,Math.min(800,camera.position.z));}});

document.getElementById('info').innerHTML = 'Geological Fossil Layers \u2014 '+LAYERS.length+' strata \u00b7 Hover for fossils';
function animate() {{
    requestAnimationFrame(animate);
    dust.rotation.y += 0.0003;
    if(SHOW_LABELS) updateLabels();
    renderer.render(scene, camera);
}}
animate();
"""
    html = _wrap_html(js, width, height)
    components.html(html, width=width, height=height + 10, scrolling=False)


def render_migration_paths(paths: list, width: int = 800, height: int = 600, show_labels: bool = False):
    """Render keyword migration path animation with trail effects and pause control."""
    js = f"""
const PATHS = {json.dumps(paths, ensure_ascii=False)};
const W={width}, H={height};
const SHOW_LABELS = {'true' if show_labels else 'false'};
let isPaused = false;
function togglePause() {{
    isPaused = !isPaused;
    const btn = document.getElementById('pause-btn');
    if(btn) btn.textContent = isPaused ? '\u25b6 Resume' : '\u23f8 Pause';
}}

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x060d1f, 0.002);
const camera = new THREE.PerspectiveCamera(50, W/H, 0.1, 2000);
camera.position.set(0, 0, 300);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W, H); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x060d1f);
document.body.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0x334455, 0.5));
scene.add(new THREE.PointLight(0x00aaff, 1, 500));

const tooltip = document.getElementById('tooltip');
const labelsContainer = document.getElementById('labels');
const labelElements = [];
const allWaypointMeshes = [];

const colors = [0x00ffaa, 0xff8844, 0x4488ff, 0xff44aa, 0xffcc00, 0x44ffcc];
const particles = [];

PATHS.forEach((path, pi) => {{
    const col = colors[pi % colors.length];
    const colHex = '#' + new THREE.Color(col).getHexString();
    const pts = (path.waypoints||[]).map(w => new THREE.Vector3(w.x||0, w.y||0, 0));
    if(pts.length < 2) return;
    const curve = new THREE.CatmullRomCurve3(pts);
    const cPts = curve.getPoints(60);
    const lmat = new THREE.LineBasicMaterial({{color: col, transparent:true, opacity:0.35}});
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(cPts), lmat));
    // Particle
    const pgeo = new THREE.SphereGeometry(3.5, 12, 12);
    const pmat = new THREE.MeshPhongMaterial({{color: col, emissive: new THREE.Color(col).multiplyScalar(0.5)}});
    const pmesh = new THREE.Mesh(pgeo, pmat);
    pmesh.position.copy(pts[0]); scene.add(pmesh);
    pmesh.userData = {{name: path.keyword, type: 'particle'}};
    allWaypointMeshes.push(pmesh);
    // Glow
    const gg = new THREE.SphereGeometry(7, 8, 8);
    const gm = new THREE.MeshBasicMaterial({{color: col, transparent:true, opacity:0.1}});
    pmesh.add(new THREE.Mesh(gg, gm));
    particles.push({{mesh: pmesh, curve, t: Math.random()*0.3, speed: 0.003 + Math.random()*0.002}});
    // Moving particle label
    if(SHOW_LABELS) {{
        const lbl = document.createElement('div');
        lbl.className = 'node-label';
        lbl.textContent = path.keyword;
        lbl.style.color = colHex;
        lbl.style.fontSize = '10px';
        lbl.style.fontWeight = 'bold';
        labelsContainer.appendChild(lbl);
        labelElements.push({{el: lbl, mesh: pmesh}});
    }}
    // Waypoint markers
    (path.waypoints||[]).forEach((w, wi) => {{
        const p = new THREE.Vector3(w.x||0, w.y||0, 0);
        const mg = new THREE.SphereGeometry(1.8, 8, 8);
        const mm = new THREE.MeshPhongMaterial({{color: col, transparent:true, opacity:0.45}});
        const m = new THREE.Mesh(mg, mm);
        m.position.copy(p); scene.add(m);
        m.userData = {{name: w.field || ('Stop ' + wi), type: 'waypoint', keyword: path.keyword, year: w.year}};
        allWaypointMeshes.push(m);
        if(SHOW_LABELS) {{
            const lbl = document.createElement('div');
            lbl.className = 'node-label';
            lbl.textContent = w.field || ('Stop ' + wi);
            lbl.style.color = colHex;
            lbl.style.fontSize = '8px';
            labelsContainer.appendChild(lbl);
            labelElements.push({{el: lbl, mesh: m}});
        }}
    }});
}});

// BG particles
const bg = new THREE.BufferGeometry(); const bc = 200;
const bp = new Float32Array(bc*3);
for(let i=0;i<bc*3;i++) bp[i]=(Math.random()-0.5)*600;
bg.setAttribute('position', new THREE.BufferAttribute(bp,3));
scene.add(new THREE.Points(bg, new THREE.PointsMaterial({{color:0x0066ff, size:0.5, transparent:true, opacity:0.2}})));

function updateLabels() {{
    labelElements.forEach(item => {{
        const pos = item.mesh.position.clone();
        pos.project(camera);
        const x = (pos.x * 0.5 + 0.5) * W;
        const y = (-pos.y * 0.5 + 0.5) * H;
        if(pos.z < 1) {{
            item.el.style.display = 'block';
            item.el.style.left = x + 'px';
            item.el.style.top = (y - 8) + 'px';
        }} else {{
            item.el.style.display = 'none';
        }}
    }});
}}

// Hover tooltip
renderer.domElement.addEventListener('mousemove', (e) => {{
    const m = new THREE.Vector2((e.offsetX/W)*2-1, -(e.offsetY/H)*2+1);
    const rc = new THREE.Raycaster(); rc.setFromCamera(m, camera);
    const h = rc.intersectObjects(allWaypointMeshes);
    if(h.length) {{
        const d = h[0].object.userData;
        tooltip.style.display='block'; tooltip.style.left=(e.offsetX+15)+'px'; tooltip.style.top=(e.offsetY+15)+'px';
        if(d.type==='particle') tooltip.innerHTML='<b>\U0001f985 '+d.name+'</b><br><span class="tag">Migrating</span>';
        else tooltip.innerHTML='<b>\U0001f4cd '+d.name+'</b><br><span class="tag">'+d.keyword+'</span>'+(d.year ? ' <span class="tag">Year: '+d.year+'</span>' : '');
    }} else tooltip.style.display='none';
}});

let drag=false,px=0,py=0;
renderer.domElement.addEventListener('mousedown',(e)=>{{drag=true;px=e.clientX;py=e.clientY;}});
renderer.domElement.addEventListener('mouseup',()=>{{drag=false;}});
renderer.domElement.addEventListener('mousemove',(e)=>{{if(drag){{scene.rotation.y+=(e.clientX-px)*0.004;px=e.clientX;py=e.clientY;}}}});
renderer.domElement.addEventListener('wheel',(e)=>{{camera.position.z+=e.deltaY*0.4;}});

document.getElementById('info').innerHTML = 'Migration Paths \u2014 '+PATHS.length+' tracked keywords \u00b7 Click Pause to freeze';
function animate() {{
    requestAnimationFrame(animate);
    if(!isPaused) {{
        particles.forEach(p => {{
            p.t += p.speed;
            if(p.t >= 1) p.t = 0;
            const pt = p.curve.getPointAt(p.t);
            p.mesh.position.copy(pt);
        }});
    }}
    if(SHOW_LABELS) updateLabels();
    renderer.render(scene, camera);
}}
animate();
"""
    html = _wrap_html(js, width, height, show_pause=True)
    components.html(html, width=width, height=height + 10, scrolling=False)


def render_niche_hierarchy(levels: list, width: int = 800, height: int = 500, show_labels: bool = False):
    """Render vertical niche hierarchy with connecting lines."""
    js = f"""
const LEVELS = {json.dumps(levels, ensure_ascii=False)};
const W={width}, H={height};
const SHOW_LABELS = {'true' if show_labels else 'false'};
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x060d1f, 0.002);
const camera = new THREE.PerspectiveCamera(50, W/H, 0.1, 2000);
camera.position.set(0, 0, 300);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W, H); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x060d1f);
document.body.appendChild(renderer.domElement);
scene.add(new THREE.AmbientLight(0x445566, 0.6));
scene.add(new THREE.PointLight(0x00ffaa, 0.9, 500));

const tooltip = document.getElementById('tooltip');
const allMeshes = [];
const labelsContainer = document.getElementById('labels');
const labelElements = [];
const levelNames = ['L1 Foundation','L2 Method','L3 Technical','L4 Application','L5 Domain'];

LEVELS.forEach((lvl, li) => {{
    const y = 90 - li * 45;
    const hue = 0.35 + li * 0.1;
    const sep = [new THREE.Vector3(-160, y-20, 0), new THREE.Vector3(160, y-20, 0)];
    const sm = new THREE.LineBasicMaterial({{color: new THREE.Color().setHSL(hue, 0.3, 0.25), transparent:true, opacity:0.4}});
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(sep), sm));
    (lvl.keywords||[]).forEach((kw, ki) => {{
        const x = (ki - (lvl.keywords.length-1)/2) * 22;
        const color = new THREE.Color().setHSL(hue, 0.75, 0.55);
        const geo = new THREE.SphereGeometry(4, 14, 14);
        const mat = new THREE.MeshPhongMaterial({{color, emissive:color.clone().multiplyScalar(0.3), shininess:60}});
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(x, y, 0);
        mesh.userData = {{name: kw, level: lvl.level, levelName: levelNames[li]||'L'+lvl.level}};
        scene.add(mesh); allMeshes.push(mesh);
        const gg = new THREE.SphereGeometry(6, 8, 8);
        mesh.add(new THREE.Mesh(gg, new THREE.MeshBasicMaterial({{color, transparent:true, opacity:0.06}})));
        if(SHOW_LABELS) {{
            const lbl = document.createElement('div');
            lbl.className = 'node-label';
            lbl.textContent = kw;
            lbl.style.color = '#' + color.getHexString();
            labelsContainer.appendChild(lbl);
            labelElements.push({{el: lbl, mesh: mesh}});
        }}
    }});
}});

function updateLabels() {{
    labelElements.forEach(item => {{
        const pos = item.mesh.position.clone();
        pos.project(camera);
        const x = (pos.x * 0.5 + 0.5) * W;
        const y = (-pos.y * 0.5 + 0.5) * H;
        if(pos.z < 1) {{
            item.el.style.display = 'block';
            item.el.style.left = x + 'px';
            item.el.style.top = (y - 8) + 'px';
        }} else {{
            item.el.style.display = 'none';
        }}
    }});
}}

renderer.domElement.addEventListener('mousemove',(e)=>{{
    const m = new THREE.Vector2((e.offsetX/W)*2-1,-(e.offsetY/H)*2+1);
    const rc = new THREE.Raycaster(); rc.setFromCamera(m,camera);
    const h = rc.intersectObjects(allMeshes);
    if(h.length){{
        const d=h[0].object.userData;
        tooltip.style.display='block';tooltip.style.left=(e.offsetX+15)+'px';tooltip.style.top=(e.offsetY+15)+'px';
        tooltip.innerHTML='<b>'+d.name+'</b><br><span class="tag">'+d.levelName+'</span>';
    }} else tooltip.style.display='none';
}});
renderer.domElement.addEventListener('wheel',(e)=>{{camera.position.z+=e.deltaY*0.4;camera.position.z=Math.max(80,Math.min(600,camera.position.z));}});
let drag=false,px=0,py=0;
renderer.domElement.addEventListener('mousedown',(e)=>{{drag=true;px=e.clientX;py=e.clientY;}});
renderer.domElement.addEventListener('mouseup',()=>{{drag=false;}});
renderer.domElement.addEventListener('mousemove',(e)=>{{if(drag){{scene.rotation.y+=(e.clientX-px)*0.004;scene.rotation.x+=(e.clientY-py)*0.004;px=e.clientX;py=e.clientY;}}}});

document.getElementById('info').innerHTML = 'Niche Hierarchy \u2014 '+LEVELS.length+' levels';
function animate(){{
    requestAnimationFrame(animate);
    if(SHOW_LABELS) updateLabels();
    renderer.render(scene,camera);
}}
animate();
"""
    html = _wrap_html(js, width, height)
    components.html(html, width=width, height=height + 10, scrolling=False)
