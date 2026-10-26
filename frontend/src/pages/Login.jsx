import{useState}from"react";
import{useNavigate,Link}from"react-router-dom";
import{useAuth}from"../context/AuthContext";
import{authAPI}from"../services/api";

const ROLES=[
  {v:"DONOR",icon:"🩸",label:"Donor"},
  {v:"CAMP_COORDINATOR",icon:"🏕️",label:"Coordinator"},
  {v:"HOSPITAL_ADMIN",icon:"🏥",label:"Hospital Admin"},
];

export default function Login(){
  const[tab,setTab]=useState("login");
  const[form,setForm]=useState({username:"",password:"",email:"",role:"DONOR"});
  const[err,setErr]=useState("");
  const[ok,setOk]=useState("");
  const[loading,setLoading]=useState(false);
  const{login}=useAuth();
  const nav=useNavigate();
  const f=k=>e=>setForm(p=>({...p,[k]:e.target.value}));

  const submit=async e=>{
    e.preventDefault(); setErr(""); setOk(""); setLoading(true);
    try{
      if(tab==="signup"){
        await authAPI.signup(form);
        setOk("Account created! Please sign in.");
        setTab("login"); setForm(p=>({...p,password:""}));
      }else{
        const{data}=await authAPI.login({username:form.username,password:form.password});
        login(data); nav("/dashboard");
      }
    }catch(e){setErr(e.response?.data?.error||"Request failed. Is the backend running?");}
    finally{setLoading(false);}
  };

  const inp={width:"100%",padding:"12px 16px",background:"#0f172a",border:"1px solid #1e293b",borderRadius:10,color:"#f1f5f9",fontSize:14,fontFamily:"inherit",outline:"none",boxSizing:"border-box"};

  return(
    <div style={{minHeight:"100vh",display:"flex",fontFamily:"'DM Sans',sans-serif"}}>
      {/* Left decorative panel */}
      <div style={{width:"45%",background:"linear-gradient(135deg,#1a0505,#0f0a0a)",display:"flex",flexDirection:"column",justifyContent:"space-between",padding:48,position:"relative",overflow:"hidden"}}>
        <div style={{position:"absolute",top:-50,left:-50,width:300,height:300,background:"radial-gradient(circle,#dc262625,transparent 70%)",borderRadius:"50%"}}/>
        <div style={{position:"absolute",bottom:-50,right:-50,width:250,height:250,background:"radial-gradient(circle,#7f1d1d30,transparent 70%)",borderRadius:"50%"}}/>
        <div style={{position:"relative",zIndex:1}}>
          <Link to="/" style={{color:"#6b7280",textDecoration:"none",fontSize:14}}>← Back to home</Link>
        </div>
        <div style={{position:"relative",zIndex:1}}>
          <div style={{fontSize:56,marginBottom:16,animation:"float 5s ease-in-out infinite"}}>🩸</div>
          <h2 style={{fontSize:36,fontWeight:700,color:"#fff",marginBottom:16,fontFamily:"'Playfair Display',serif",lineHeight:1.2}}>
            {tab==="login"?"Welcome back.":"Join the mission."}
          </h2>
          <p style={{color:"#6b7280",fontSize:15,lineHeight:1.7,marginBottom:32}}>
            {tab==="login"?"Your dashboard awaits. Real-time stock, donor predictions, camp management.":"Every registered donor brings us closer to zero blood shortage."}
          </p>
          {["AI-powered shortage prediction","Real-time stock alerts","4 role-based dashboards"].map((f,i)=>(
            <div key={i} style={{display:"flex",alignItems:"center",gap:10,marginBottom:10}}>
              <div style={{width:20,height:20,background:"#dc262620",border:"1px solid #dc262640",borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,color:"#f87171",flexShrink:0}}>✓</div>
              <span style={{fontSize:13,color:"#9ca3af"}}>{f}</span>
            </div>
          ))}
        </div>
        <div style={{position:"relative",zIndex:1,fontSize:12,color:"#374151"}}>© 2024 BloodBank Pro</div>
      </div>

      {/* Right form panel */}
      <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center",padding:48,background:"#030712"}}>
        <div style={{width:"100%",maxWidth:420}} className="fade-up">
          {/* Tabs */}
          <div style={{display:"flex",background:"#0f172a",borderRadius:12,padding:4,marginBottom:32}}>
            {["login","signup"].map(t=>(
              <button key={t} onClick={()=>{setTab(t);setErr("");setOk("");}}
                style={{flex:1,padding:"10px",borderRadius:8,border:"none",cursor:"pointer",fontFamily:"inherit",fontSize:14,fontWeight:500,
                  background:tab===t?"#1e293b":"transparent",color:tab===t?"#f1f5f9":"#6b7280",transition:"all .2s"}}>
                {t==="login"?"Sign In":"Sign Up"}
              </button>
            ))}
          </div>

          {/* Test credentials box */}
          {tab==="login"&&(
            <div>
              <p style={{color:"#94a3b8",marginBottom:6,fontWeight:500}}></p>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:4,color:"#64748b"}}>
              </div>
            </div>
          )}

          <form onSubmit={submit}>
            <div style={{marginBottom:16}}>
              <label style={{display:"block",fontSize:13,color:"#94a3b8",marginBottom:6}}>Username</label>
              <input style={inp} type="text" required placeholder="Enter username" value={form.username} onChange={f("username")} onFocus={e=>e.target.style.borderColor="#dc2626"} onBlur={e=>e.target.style.borderColor="#1e293b"}/>
            </div>
            {tab==="signup"&&(
              <div style={{marginBottom:16}}>
                <label style={{display:"block",fontSize:13,color:"#94a3b8",marginBottom:6}}>Email</label>
                <input style={inp} type="email" required placeholder="your@email.com" value={form.email} onChange={f("email")} onFocus={e=>e.target.style.borderColor="#dc2626"} onBlur={e=>e.target.style.borderColor="#1e293b"}/>
              </div>
            )}
            <div style={{marginBottom:16}}>
              <label style={{display:"block",fontSize:13,color:"#94a3b8",marginBottom:6}}>Password</label>
              <input style={inp} type="password" required placeholder="••••••••" value={form.password} onChange={f("password")} onFocus={e=>e.target.style.borderColor="#dc2626"} onBlur={e=>e.target.style.borderColor="#1e293b"}/>
            </div>
            {tab==="signup"&&(
              <div style={{marginBottom:20}}>
                <label style={{display:"block",fontSize:13,color:"#94a3b8",marginBottom:8}}>Select Role</label>
                <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
                  {ROLES.map(r=>(
                    <label key={r.v} style={{display:"flex",alignItems:"center",gap:8,padding:"10px 12px",borderRadius:10,cursor:"pointer",
                      background:form.role===r.v?"#7f1d1d30":"#0f172a",border:`1px solid ${form.role===r.v?"#dc262660":"#1e293b"}`,transition:"all .2s"}}>
                      <input type="radio" name="role" style={{display:"none"}} checked={form.role===r.v} onChange={()=>setForm(p=>({...p,role:r.v}))}/>
                      <span style={{fontSize:16}}>{r.icon}</span>
                      <span style={{fontSize:12,color:form.role===r.v?"#fca5a5":"#6b7280",fontWeight:500}}>{r.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
            {err&&<div style={{background:"#7f1d1d20",border:"1px solid #dc262640",borderRadius:8,padding:"10px 14px",fontSize:13,color:"#fca5a5",marginBottom:16}}>⚠ {err}</div>}
            {ok&&<div style={{background:"#14532d20",border:"1px solid #16a34a40",borderRadius:8,padding:"10px 14px",fontSize:13,color:"#86efac",marginBottom:16}}>✓ {ok}</div>}
            <button type="submit" disabled={loading}
              style={{width:"100%",padding:"13px",background:"#dc2626",border:"none",borderRadius:10,color:"#fff",fontSize:15,fontWeight:600,cursor:"pointer",fontFamily:"inherit",boxShadow:"0 4px 20px #dc262640",opacity:loading?.7:1,transition:"all .2s"}}>
              {loading?"Please wait...":(tab==="login"?"Sign In →":"Create Account →")}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
