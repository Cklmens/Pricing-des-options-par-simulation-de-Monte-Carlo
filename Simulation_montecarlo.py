
import numpy as np
import streamlit as st
import math as ma
from bokeh.plotting import figure
import matplotlib.pyplot as plt
from scipy.stats import norm
import scipy.stats as stat
from scipy.stats import norm
import math as ma
import pandas as pd

st.set_page_config(
    page_title="Simulation de MonteCarlo",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",   
)
# fonction de simulation de la loi normal
def simulation_loinormal(nb_variable,mean,std) :
    norm=np.ones(nb_variable)
    unif1=np.random.uniform(low=0.0, high=1.0, size=nb_variable)
    unif2=np.random.uniform(low=0.0, high=1.0, size=nb_variable)
    for i in range(nb_variable):
        norm[i]=(ma.sqrt(-ma.log2(unif1[i]))*ma.cos(2*ma.pi*unif2[i]) + ma.sqrt(-ma.log2((1-unif1[i])))*ma.cos(2*ma.pi*(1-unif2[i])))/2
        norm[i]= std*norm[i]+mean
    return norm
# fonction de simulation du mouvement browmien
def mvt_browmien(N):
   browm=np.zeros(N)
   n=simulation_loinormal(N,0,1)
   T=1 #période en année
   dt=T/N
   for i in range(1,N):
      browm[i]=browm[i-1]+ ma.sqrt(dt)*n[i-1]
   return browm
# fonction d'affichage de l'évolutinon des prix
def plot_St(const,So,T,sigma,r):
   N=100
   norm_Va1=np.random.normal(0,1,(const,N))   
  
   # T période en année
   dt=T/N
   #Simulation du mouvement browmien: browm
   browm1=np.zeros((const,N))
   for j in range(const):
      for i in range(1,N):
        browm1[j][i]=browm1[j][i-1]+ ma.sqrt(dt)*norm_Va1[j][i-1]
   
   St1=np.zeros((const,N))
   for j in range(const):
      for i in range(N):
       St1[j][i] = So*ma.exp((r-(sigma**2)/2)*dt + sigma*browm1[j][i])
      plt.plot(St1[j])
      plt.xlabel("nombre de subdivisions du temps")
      plt.ylabel('Prix du sous-jacent')
      
   return(plt.show())
# fonction de determination du prix du call europenne et des grecques et la var
def prix_St_browm(const,N,So,K,T,sigma,r,style,alpha):
   norm_Va1=np.random.normal(0,1,(const,N))
      
  #Simulation du mouvement browmien: browm
   browm1=np.zeros((const,N))
   browm2=np.zeros((const,N))
   # T période en année
   dt=T/N
   for j in range(const):
      for i in range(1,N):
        browm1[j][i]= browm1[j][i-1]+ma.sqrt(dt)*norm_Va1[j][i-1]  #
        browm2[j][i]= browm2[j][i-1]-ma.sqrt(dt)*norm_Va1[j][i-1] #
      
   St1=np.zeros((const))
   St2=np.zeros((const))
   for j in range(const):
       St1[j] = So*ma.exp((r-(sigma**2)/2)*T + sigma*browm1[j][-1])
       St2[j] = So*ma.exp((r-(sigma**2)/2)*T + sigma*browm2[j][-1])

   payoff=np.ones(const)
   if (style=="call"):

      for i in range(const):
        payoff[i]=((max((St1[i]-K),0))*ma.exp(-r*T)+ (max((St2[i]-K),0))*ma.exp(-r*T))/2
        
      return("Valeur de l'option pour "+str(const)+" Simulations est: "+str(np.mean(payoff))+"  +/-  "+str((norm.cdf(alpha)*np.std(payoff))/np.sqrt(const)))
   if(style=='put'):
      for i in range(const):       
        payoff[i]=((max(K-(St1[i]),0))*ma.exp(-r*T)+ (max(K-(St2[i]),0))*ma.exp(-r*T))/2
       
      return("Valeur de l'option pour "+str(const)+" Simulations est: "+str(np.mean(payoff))+"  +/-  "+str((norm.cdf(alpha)*np.std(payoff))/np.sqrt(const)))
      
def prix_St_norm0(const,So,K,T,sigma,r,style,alpha):
  browm1=  np.random.normal(0,1,const)
  St1=np.zeros((const))
  St2=np.zeros((const))
  for j in range(const):
    St1[j] = So*ma.exp((r-(sigma**2)/2)*T + sigma*ma.sqrt(T)*browm1[j])
    St2[j]= So*ma.exp((r-(sigma**2)/2)*T - sigma*ma.sqrt(T)*browm1[j])   
  payoff=np.ones(const)
  if (style=="call"):
    for i in range(const):
      payoff[i]=((max((St1[i]-K),0)+ (max((St2[i]-K),0)))*ma.exp(-r*T))/2
    return("Valeur de l'option pour "+str(const)+" Simulations est: "+str(np.mean(payoff))+" +/- "+str((norm.cdf(alpha)*np.std(payoff))/np.sqrt(const)))
  if(style=='put'):
      for i in range(const):       
         payoff[i]=((max(K-(St1[i][-1]),0))*ma.exp(-r*T)+ (max(K-(St2[i][-1]),0))*ma.exp(-r*T))/2
      return("Valeur de l'option pour "+str(const)+" Simulations est: "+str(np.mean(payoff)/2)+" +/- "+str((norm.cdf(alpha)*np.std(payoff))/np.sqrt(const)))

def qmc_simulation(M,d=1):
    qmc_= stat.qmc.Sobol(d, scramble=True) 
    x_sobol= qmc_.random_base2(M)
    return stat.norm.ppf(x_sobol)

def prix_St_norm(So,K,T,sigma,r,style):
  const=len(qmc_simulation(11))
  browm1=  qmc_simulation(11)
  St1=np.zeros((const))
  St2=np.zeros((const))
  St1 = So*np.exp((r-(sigma**2)/2)*T + sigma*ma.sqrt(T)*browm1)
  St2 = So*np.exp((r-(sigma**2)/2)*T - sigma*ma.sqrt(T)*browm1)       
  payoff=np.ones(const)
  #Variable de controle
  Z=0.5*np.exp(-r*T)*(St1+St2)
  if (style=="call"):
    for i in range(const):
      payoff[i]=((max((St1[i]-K),0)+ (max((St2[i]-K),0)))*ma.exp(-r*T))/2       
  if(style=='put'):
      for i in range(const):       
         payoff[i]=((max((K-St1[i]),0)+ (max((K-St2[i]),0)))*ma.exp(-r*T))/2    
  k=-np.cov(Z.T,payoff)/np.var(Z)
  variable_de_controle= payoff +k[0][1]*(Z-np.mean(Z))
  return np.mean(variable_de_controle)#, 1.96*np.std(variable_de_controle)/const, const   
def delta(So,K,T,sigma,r,style):
  h=1
  return (prix_St_norm(So-2*h,K,T,sigma,r,style)- 8*(prix_St_norm(So-h,K,T,sigma,r,style)) +8*prix_St_norm(So+h,K,T,sigma,r,style)-prix_St_norm(So+2*h,K,T,sigma,r,style))/(12*h)
def gamma(So,K,T,sigma,r,style):
  h=1
  return (delta(So-2*h,K,T,sigma,r,style)- 8*(delta(So-h,K,T,sigma,r,style)) +8*delta(So+h,K,T,sigma,r,style)-delta(So+h,K,T,sigma,r,style))/(12*h)
def theta(So,K,T,sigma,r,style):
  t=T/100
  return (prix_St_norm(So,K,T-2*t,sigma,r,style)- 8*(prix_St_norm(So,K,T-t,sigma,r,style)) +8*prix_St_norm(So,K,T+t,sigma,r,style)-prix_St_norm(So,K,T+2*t,sigma,r,style))/(12*t)
def rho(So,K,T,sigma,r,style):
  
  h=0.001
  return (prix_St_norm(So,K,T,sigma,r-2*h,style) - 8*(prix_St_norm(So,K,T,sigma,r-h,style)) + 8*prix_St_norm(So,K,T,sigma,r+h,style) - prix_St_norm(So,K,T,sigma,r+2*h,style))/(12*h)
def vega(So,K,T,sigma,r,style):
  h=sigma/100
  return (prix_St_norm(So,K,T,sigma-2*h,r,style)- 8*(prix_St_norm(So,K,T,sigma-h,r,style)) +8*prix_St_norm(So,K,T,sigma+h,r,style)-prix_St_norm(So,K,T,sigma+2*h,r,style))/(12*h)
def var_montecarlo_europene(So,K,To,sigma,r,style,level=0.05):
  const=100000
  browm1=  np.random.normal(0,1,const)
  St1=np.zeros((const))
  St2=np.zeros((const))
  T= 14/365 
  St1 = So*np.exp((r-(sigma**2)/2)*T + sigma*ma.sqrt(T)*browm1)
  St2 = So*np.exp((r-(sigma**2)/2)*T - sigma*ma.sqrt(T)*browm1)   
  T= T/365    
  payoff=np.ones(const)
  Z=0.5*np.exp(-r*T)*(St1+St2)
  if (style=="call"):
    for i in range(const):
      payoff[i]=((max((St1[i]-K*ma.exp(-r*(To-T))),0)+ (max((St2[i]-K*ma.exp(-r*(To-T))),0)))*ma.exp(-r*T))/2  
  if(style=='put'):
      for i in range(const):       
         payoff[i]=((max((K*ma.exp(-r*(To-T))-St1[i]),0)+ (max((K*ma.exp(-r*(To-T))-St2[i]),0)))*ma.exp(-r*T))/2
  k=-np.cov(Z.T,payoff)/np.var(Z)

  vc= payoff +k[0][1]*(Z-np.mean(Z))   
  var=np.percentile(vc, level)
  cvar=pd.DataFrame(vc)[pd.DataFrame(vc)<= var].mean() 
  return var,cvar
def delta_gamma(So,K,To,sigma,r,style, alpha=0.05):
  d=delta_BS(So,K,To,r,sigma,style)
  g=gamma_BS(So,K,To,r,sigma,style)
  t=theta_BS(So,K,To,r,sigma,style)
  const=len(qmc_simulation(17))
  browm1=  qmc_simulation(17)
  St1=np.zeros((const))
  T= 1.4/365 
  St1 = So- So*np.exp((r-(sigma**2)/2)*T + sigma*ma.sqrt(T)*browm1)
  delta_c= St1*d +0.5*(St1**2)*g + T*t
  var=np.percentile(delta_c, 1-alpha)
  cvar=pd.DataFrame(delta_c)[pd.DataFrame(delta_c)<= var].mean().to_numpy()
  return var, cvar
#Modèle de black and Scholes
def black_scholes(S,K,T,r,sigma, style):
    d1 = (np.log(S/K) + (r  + sigma**2/2)*T) / sigma*np.sqrt(T)
    d2 = d1 - sigma* np.sqrt(T)
    if (style=='call'):
        return S * norm.cdf(d1)  - K * np.exp(-r*T)*norm.cdf(d2)
    if(style=='put'):
        return K * np.exp(-r*T)*norm.cdf(-d2)-S * norm.cdf(-d1)
def delta_BS(S,K,T,r,sigma, style):
    d1=(ma.log(S/K)+(r+(sigma**2)/2)*T)/(sigma*ma.sqrt(T))
    if(style=='call'):
       return norm.cdf(d1)
    if(style=='put'):
       return norm.cdf(d1)-1
def gamma_BS(S,K,T,r,sigma,style):
    d1=(ma.log(S/K)+(r+(sigma**2)/2)*T)/(sigma*ma.sqrt(T))
    return (norm.pdf(d1)/(S*sigma*ma.sqrt(T)))
def theta_BS(S,K,T,r,sigma,style):
    d1=(ma.log(S/K)+(r+(sigma**2)/2)*T)/(sigma*ma.sqrt(T))
    d2=d1-sigma*ma.sqrt(T)
    if(style=='call'):
      return ((-(S*sigma*norm.pdf(d1))/(2*ma.sqrt(T)))-K*r*ma.exp(-r*T)*norm.cdf(d2))
    if(style=='put'):
      return (-(S*sigma*norm.pdf(d1))/(2*ma.sqrt(T))+K*r*ma.exp(-r*T)*norm.cdf(-d2))

#Option Asiatique - Grecques - VaR et CVaR

def option_asiatique(So,K,T,sigma,r,style):
  const=len(qmc_simulation(10))
  browm1=  qmc_simulation(10)
  St1=np.zeros((const))
  St2=np.zeros((const))
  dis=300
  t=np.arange(0,T+T/dis, T/dis)
  for i in range(dis+1):
    St1 = St1 + So*np.exp((r-(sigma**2)/2)*t[i] + sigma*ma.sqrt(t[i])*browm1)
    St2 = St2 + So*np.exp((r-(sigma**2)/2)*t[i] - sigma*ma.sqrt(t[i])*browm1) 
  St1=St1[:,0]/dis   
  St2=St2[:,0]/dis      
  payoff=np.ones(const)
  #Variable de controle
  Z=0.5*np.exp(-r*T)*(St1+St2)
  if (style=="call"):
    for i in range(const):
      payoff[i]=((max((St1[i]-K),0)+ (max((St2[i]-K),0)))*ma.exp(-r*T))/2       
  if(style=='put'):
      for i in range(const):       
         payoff[i]=((max((K-St1[i]),0)+ (max((K-St2[i]),0)))*ma.exp(-r*T))/2    
  k=-np.cov(Z.T,payoff)/np.var(Z)
  variable_de_controle= payoff +k[0][1]*(Z-np.mean(Z))
  return  np.mean(variable_de_controle)
def delta_asiatique(So,K,T,sigma,r,style):
  h=1
  return (option_asiatique(So-2*h,K,T,sigma,r,style)- 8*(option_asiatique(So-h,K,T,sigma,r,style)) +8*option_asiatique(So+h,K,T,sigma,r,style)-option_asiatique(So+2*h,K,T,sigma,r,style))/(12*h)
def gamma_asiatique(So,K,T,sigma,r,style):
  h=1
  return (delta_asiatique(So-2*h,K,T,sigma,r,style)- 8*(delta_asiatique(So-h,K,T,sigma,r,style)) +8*delta_asiatique(So+h,K,T,sigma,r,style)-delta_asiatique(So+h,K,T,sigma,r,style))/(12*h)
def theta_asiatique(So,K,T,sigma,r,style):
  t=T/100
  return (option_asiatique(So,K,T-2*t,sigma,r,style)- 8*(option_asiatique(So,K,T-t,sigma,r,style)) +8*option_asiatique(So,K,T+t,sigma,r,style)-option_asiatique(So,K,T+2*t,sigma,r,style))/(12*t)
def rho_asiatique(So,K,T,sigma,r,style):
  h=0.001
  return (option_asiatique(So,K,T,sigma,r-2*h,style) - 8*(option_asiatique(So,K,T,sigma,r-h,style)) + 8*option_asiatique(So,K,T,sigma,r+h,style) - option_asiatique(So,K,T,sigma,r+2*h,style))/(12*h)
def vega_asiatique(So,K,T,sigma,r,style):
  h=sigma/100
  return (option_asiatique(So,K,T,sigma-2*h,r,style)- 8*(option_asiatique(So,K,T,sigma-h,r,style)) +8*option_asiatique(So,K,T,sigma+h,r,style)-option_asiatique(So,K,T,sigma+2*h,r,style))/(12*h)
def delta_gamma_asiatique(So,K,To,sigma,r,style, alpha=0.05):
  d=delta_asiatique(So,K,To,r,sigma,style)
  g=gamma_asiatique(So,K,To,r,sigma,style)
  theta=theta_asiatique(So,K,To,r,sigma,style)
  const=len(qmc_simulation(8))
  browm1=  qmc_simulation(8)
  St1=np.zeros((const))
  T= 1.4/365 
  dis=100
  t=np.arange(0,T+T/dis, T/dis)
  for i in range(dis+1):
    St1 = St1 + So*np.exp((r-(sigma**2)/2)*t[i] + sigma*ma.sqrt(t[i])*browm1)
  St1=St1[:,0]/dis
  St1 = So- St1
  delta_c= St1*d +0.5*(St1**2)*g + T*theta
  var=np.percentile(delta_c, 1-alpha)
  cvar=pd.DataFrame(delta_c)[pd.DataFrame(delta_c)<= var].mean().to_numpy()
  return var, cvar

#Option Lookback - Grecques - VaR et CVaR

def option_lookback(So,K,T,sigma,r,style):
  const=len(qmc_simulation(12))
  browm1=  qmc_simulation(12)
  dis=300
  St1=np.zeros((const,dis+1))
  St2=np.zeros((const, dis+1))
 
  t=np.arange(0,T+T/dis, T/dis)
  for i in range(dis+1):
    St1[:,i:i+1] = So*np.exp((r-(sigma**2)/2)*t[i] + sigma*ma.sqrt(t[i])*browm1)
    St2[:,i:i+1]= So*np.exp((r-(sigma**2)/2)*t[i] - sigma*ma.sqrt(t[i])*browm1)  
  St1=np.mean(St1, axis=1)
  St2=np.mean(St2, axis=1)
  if (style=="call"):
      payoff=((max((np.amax(St1)-K),0)+ (max((np.amax(St1)-K),0)))*ma.exp(-r*T))/2       
  if(style=='put'): 
      payoff=((max((K-np.amin(St1)),0)+ (max(min(K-np.ammin(St2)),0)))*ma.exp(-r*T))/2    
  return  payoff
def delta_lookback(So,K,T,sigma,r,style):
  h=1
  return (option_lookback(So-2*h,K,T,sigma,r,style)- 8*(option_lookback(So-h,K,T,sigma,r,style)) +8*option_lookback(So+h,K,T,sigma,r,style)-option_lookback(So+2*h,K,T,sigma,r,style))/(12*h)
def gamma_lookback(So,K,T,sigma,r,style):
  h=1
  return (delta_lookback(So-2*h,K,T,sigma,r,style)- 8*(delta_lookback(So-h,K,T,sigma,r,style)) +8*delta_lookback(So+h,K,T,sigma,r,style)-delta_lookback(So+h,K,T,sigma,r,style))/(12*h)
def theta_lookback(So,K,T,sigma,r,style):
  t=T/100
  return (option_lookback(So,K,T-2*t,sigma,r,style)- 8*(option_lookback(So,K,T-t,sigma,r,style)) +8*option_lookback(So,K,T+t,sigma,r,style)-option_lookback(So,K,T+2*t,sigma,r,style))/(12*t)
def rho_lookback(So,K,T,sigma,r,style):
  
  h=0.001
  return (option_lookback(So,K,T,sigma,r-2*h,style) - 8*(option_lookback(So,K,T,sigma,r-h,style)) + 8*option_lookback(So,K,T,sigma,r+h,style) - option_lookback(So,K,T,sigma,r+2*h,style))/(12*h)
def vega_lookback(So,K,T,sigma,r,style):
  h=sigma/100
  return (option_lookback(So,K,T,sigma-2*h,r,style)- 8*(option_lookback(So,K,T,sigma-h,r,style)) +8*option_lookback(So,K,T,sigma+h,r,style)-option_lookback(So,K,T,sigma+2*h,r,style))/(12*h)
def delta_gamma_lookback(So,K,To,sigma,r,style, alpha=0.05):
  d=delta_lookback(So,K,To,r,sigma,style)
  g=gamma_lookback(So,K,To,r,sigma,style)
  theta=theta_lookback(So,K,To,r,sigma,style)
  const=len(qmc_simulation(15))
  browm1=  qmc_simulation(15)
  T= 1.4/365 
  dis=100
  St1=np.zeros((const, dis+1))

  t=np.arange(0,T+T/dis, T/dis)
  for i in range(dis+1):
    St1[:,i:i+1] = So*np.exp((r-(sigma**2)/2)*t[i] + sigma*ma.sqrt(t[i])*browm1)
  St1 =  np.max(St1,axis=1 )-So
  delta_c= St1*d +0.5*(St1**2)*g + T*theta
  var=np.percentile(delta_c, 1-alpha)
  cvar=pd.DataFrame(delta_c)[pd.DataFrame(delta_c)<= var].mean().to_numpy()
  return var, cvar

#Option barriere - Grecques - VaR et CVaR 
def option_barrier(So,K,H,T,sigma,r,style):
  const=len(qmc_simulation(13))
  browm1=  qmc_simulation(13)
  dis=100
  St1=np.zeros((const,dis+1))
  St2=np.zeros((const, dis+1))
  t=np.arange(0,T+T/dis, T/dis)
  for i in range(dis+1):
    St1[:,i:i+1] = So*np.exp((r-(sigma**2)/2)*t[i] + sigma*ma.sqrt(t[i])*browm1)
    St2[:,i:i+1]= So*np.exp((r-(sigma**2)/2)*t[i] - sigma*ma.sqrt(t[i])*browm1)       
  St1=np.mean(St1, axis=1)
  St2=np.mean(St2, axis=1)
  print(np.amax(St1),np.amax(St2))
  if (np.amax(St1)< H) and (np.amax(St2)< H):
    return prix_St_norm(So,K,T,sigma,r,style)
  return 0
def delta_gamma_barrier(So,K,H,T,sigma,r,style, alpha=0.05):
  if option_barrier(So,K,H,T,sigma,r,style) :
    return delta_gamma(So,K,T,sigma,r,style, alpha=0.05)
  else:
    return 0


# Portefeuille    

st.title(" Pricing d'une option européenne par la méthode de Monte Carlo")
st.write("La simulation de Monte-Carlo est une méthode d’estimation d’une quantité numérique en utilisant des procédés aléatoires. Elle consiste à simuler plusieurs une variable aléatoire de manière indépendante et à prendre la moyenne")

with st.sidebar: 
   st.sidebar.title("Type d'option")
   type=st.sidebar.radio("les options",["Européenne","Asiatique","Lookback", "Barriere","Portefeuille"])
  

  
with st.form("Simulation Loi nomarle"):
   st.subheader("Simulation de la loi normal")
   mean=st.number_input("moyenne",step=1,value=0)
   std=st.number_input("Ecart-type",value=1)
   nb_variable=st.slider("nombre de variables",1,1000)
   submitted = st.form_submit_button("Submit")
   if (submitted):
      n=simulation_loinormal(nb_variable,mean,std)
      st.write(n)
      st.write(nb_variable,"Simulation de la loi normale de moyenne ",mean," et d'écart-type : ",std)
      v=np.ones(nb_variable)
      for i in range(nb_variable):
        v[i]=(ma.exp(-((mean-n[i])**2)/(2*(std**2))))/(std*ma.sqrt(2*ma.pi))
      fig, ax = plt.subplots()
      ax.hist(v, bins=range(min(v),max(v)), density=False )
      #ax.scatter(n,v) 
      st.pyplot(fig)
   
   
with st.form("Simulation du mouvement browmien"):
   st.subheader("Simulation du mouvement browmien")
   nb_variable=st.slider("nombre de variables",1,100)
   submitted = st.form_submit_button("Submit")
   if (submitted):
      st.write(mvt_browmien(nb_variable))
      st.line_chart(mvt_browmien(nb_variable))



if( type != "Portefeuille"):
 with st.form("Parametre de l'option"):
   st.write("Parametres: ")
   c_p=st.selectbox("Style de l'option", ["call","put"])
   So=st.number_input("Le prix initial de votre Sous-jacent",step=1)
   K=st.number_input("Le Strike",step=1)
   T=st.number_input("Temps en année",step=0.05)
   sigma=st.number_input("La volatilité",step=0.05)
   r=st.number_input("Taux sans risque",step=0.05)
   const=10000
   alpha=st.number_input(" Niveau de risque",step=0.01, value=0.05)
   submitted = st.form_submit_button("Submit")
   if(type=="Européenne"):
     if (submitted):
      st.write("Evolution possible du prix du sous-jacent pour "+str(const) + " simulations" )
      st.subheader("La valeur de l'option")
      st.write("Prix de l'option par Monte-Carlo",prix_St_norm(So,K,T,sigma,r,c_p))
      st.write("La valeur de l'option par  black and Scholes: ",black_scholes(So,K,T,r,sigma,c_p))
      st.subheader("Les grecques")
      st.write("Delta:",delta(So,K,T,sigma,r,c_p))
      st.write("gamma:",gamma(So,K,T,sigma,r,c_p))
      st.write("vega:",vega(So,K,T,sigma,r,c_p))
      st.write("theta:",theta(So,K,T,sigma,r,c_p))
      st.write("rho", rho(So,K,T,sigma,r,c_p))
      st.subheader("La Value At Risque")
      var=var_montecarlo_europene(So,K,T,sigma,r,c_p)
      d_g=delta_gamma(So,K,T,sigma,r,c_p)
      st.write("Value At Risque simulé: ", var[0], "La VaR conditionnelle simulée: ",var[1][0])
      st.write("Value At Risque Delta-Gamma: ",d_g[0], "La VaR conditionnelle Delta-Gamma: ",d_g[1][0])
   if(type=="Asiatique"):
     if (submitted):
      st.write("Evolution possible du prix du sous-jacent pour "+str(2**12) + " simulations" )
      st.subheader("La valeur de l'option")
      st.write("Prix de l'option par Monte-Carlo",option_asiatique(So,K,T,sigma,r,c_p))
      st.subheader("Les grecques")
      st.write("Delta:",delta_asiatique(So,K,T,sigma,r,c_p))
      st.write("gamma:",gamma_asiatique(So,K,T,sigma,r,c_p))
      st.write("vega:",vega_asiatique(So,K,T,sigma,r,c_p))
      st.write("theta:",theta_asiatique(So,K,T,sigma,r,c_p))
      st.write("rho", rho_asiatique(So,K,T,sigma,r,c_p))
      st.subheader("La Value At Risque")
      d_g=delta_gamma_asiatique(So,K,T,sigma,r,c_p)
      st.write("Value At Risque Delta-Gamma: ",d_g[0], "La VaR conditionnelle Delta-Gamma: ",d_g[1][0])
   if(type=="Lookback"):
     if (submitted):
      st.write("Evolution possible du prix du sous-jacent pour "+str(2**12) + " simulations" )
      st.subheader("La valeur de l'option")
      st.write("Prix de l'option par Monte-Carlo",option_lookback(So,K,T,sigma,r,c_p))
      st.subheader("Les grecques")
      st.write("Delta:",delta_lookback(So,K,T,sigma,r,c_p))
      st.write("gamma:",gamma_lookback(So,K,T,sigma,r,c_p))
      st.write("vega:",vega_lookback(So,K,T,sigma,r,c_p))
      st.write("theta:",theta_lookback(So,K,T,sigma,r,c_p))
      st.write("rho", rho_lookback(So,K,T,sigma,r,c_p))
      st.subheader("La Value At Risque")
      d_g=delta_gamma_lookback(So,K,T,sigma,r,c_p)
      st.write("Value At Risque Delta-Gamma: ",d_g[0], "La VaR conditionnelle Delta-Gamma: ",d_g[1][0])
   if(type=="Barriere"):
     H=st.number_input("La barriere",step=1)
     if (submitted):
      st.write("Evolution possible du prix du sous-jacent pour "+str(2**12) + " simulations" )
      st.subheader("La valeur de l'option")
      op=option_barrier(So,K,H,T,sigma,r,c_p)
      st.write("Prix de l'option par Monte-Carlo",op)
      st.subheader("Les grecques")
      d_g=delta_gamma_barrier(So,K,H,T,sigma,r,c_p)
      if(op != 0):
        st.write("Delta:",delta(So,K,T,sigma,r,c_p))
        st.write("gamma:",gamma(So,K,T,sigma,r,c_p))
        st.write("vega:",vega(So,K,T,sigma,r,c_p))
        st.write("theta:",theta(So,K,T,sigma,r,c_p))
        st.write("rho", rho(So,K,T,sigma,r,c_p))
        st.write("Value At Risque Delta-Gamma: ",d_g[0], "La VaR conditionnelle Delta-Gamma: ",d_g[1][0])
      else:
       st.write("Delta:",0)
       st.write("gamma:",0)
       st.write("vega:",0)
       st.write("theta:",0)
       st.write("rho",0) 
       st.subheader("La Value At Risque")
       st.write("Value At Risque Delta-Gamma: ",0, "La VaR conditionnelle Delta-Gamma: ",0)
if(type=="Portefeuille"):
     with st.form("Option Européenne"):
       st.write("Option Européenne")
       n_e=st.number_input("Le nombre d'option (E) ",step=1)
       c_p_e=st.selectbox("Style de l'option (E)", ["call","put"])
       So_e=st.number_input("Le prix Sous-jacent (E)",step=1)
       K_e=st.number_input("Le Strike (E)",step=1)
       T_e=st.number_input("Temps en année (E)",step=0.05)
       sigma_e=st.number_input("La volatilité(E)",step=0.05)
       r_e=st.number_input("Taux sans risque(E)",step=0.05)

       st.write("Option Asiatique")
       n_a=st.number_input("Le nombre (A)",step=1)
       c_p_a=st.selectbox("Style de l'option (A)", ["call","put"])
       So_a=st.number_input("Le prix initial de votre Sous-jacent (A)",step=1)
       K_a=st.number_input("Le Strike (A)",step=1)
       T_a=st.number_input("Temps en année (A)",step=0.05)
       sigma_a=st.number_input("La volatilité (A)",step=0.05)
       r_a=st.number_input("Taux sans risque (A)",step=0.05)  

       st.write("Option Lookback")
       n_l=st.number_input("Le nombre (LB)",step=1)
       c_p_l=st.selectbox("Style de l'option (LB)", ["call","put"])
       So_l=st.number_input("Le prix initial de votre Sous-jacent (LB)",step=1)
       K_l=st.number_input("Le Strike (LB)",step=1)
       T_l=st.number_input("Temps en année (LB)",step=0.05)
       sigma_l=st.number_input("La volatilité (LB)",step=0.05)
       r_l=st.number_input("Taux sans risque (LB)",step=0.05)  
   
       st.write("Option Barriere")
       n_b=st.number_input("Le nombre (B)",step=1)
       c_p_b=st.selectbox("Style de l'option (B)", ["call","put"])
       So_b=st.number_input("Le prix initial de votre Sous-jacent (B)",step=1)
       K_b=st.number_input("Le Strike (B)",step=1)
       H_b=st.number_input("La Barriere (B)",step=1)
       T_b=st.number_input("Temps en année (B)",step=0.05)
       sigma_b=st.number_input("La volatilité (B)",step=0.05)
       r_b=st.number_input("Taux sans risque (B)",step=0.05) 

       submitted = st.form_submit_button("Submit")
      
     if(submitted):
        valeur=n_e*prix_St_norm(So_e,K_e,T_e,sigma_e,r_e, c_p_e) +n_a*option_asiatique(So_a,K_a,T_a,sigma_a,r_a, c_p_a)+ n_l*option_lookback(So_l,K_l,T_l,sigma_l,r_l, c_p_l)+ n_b*option_barrier(So_b,K_b,H_b,T_b,sigma_b,r_b, c_p_b)
        st.write(" valeur du portefeuille: ",valeur)
        #var= n_e*delta_gamma(So_e,K_e,T_e,sigma_e,r_e, c_p_e)[0]+ n_a*delta_gamma_asiatique(So_a,K_a,T_a,sigma_a,r_a, c_p_a)[0] + n_l*delta_gamma_lookback(So_l,K_l,T_l,sigma_l,r_l, c_p_l)[0] + n_b*delta_gamma_barrier(So_b,K_b,H_b,T_b,sigma_b,r_b, c_p_b)[0]
        vare= n_e*delta_gamma(So_e,K_e,T_e,sigma_e,r_e, c_p_e)+ n_a*delta_gamma_asiatique(So_a,K_a,T_a,sigma_a,r_a, c_p_a) + n_l*delta_gamma_lookback(So_l,K_l,T_l,sigma_l,r_l, c_p_l) + n_b*delta_gamma_barrier(So_b,K_b,H_b,T_b,sigma_b,r_b, c_p_b)
        st.write(" La VaR du portefeuille: ",vare[0])
        st.write(" La CVaR du portefeuille: ",vare[1][0])

      
   



          

   

# Simulation_montecarlo.py