import React, {useEffect, useState} from 'react';
import './css/Main.css';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import Orders from './orders';
import Stats from './stats';

const Main = () => {
    const navigate = useNavigate();
    const [component, setComponent] = useState("orders");
    let cookieValue = Cookies.get('isLoggedIn');
    let ShowComponent = Orders;
    
    useEffect(() => {
        let resp;
        const sendCheck = async () =>{
            resp = await axios.post("http://192.168.56.1:8000/api/validate/check/isLoggedIn",{
                email: cookieValue
            });
            if(resp.status !== 200) navigate('/');
        }

        if (cookieValue === undefined) {
            sendCheck();
        }
    }, [cookieValue, navigate]);

    const changeToOrders = () => setComponent("orders");
    const changeToStats =() => setComponent("stats");

    switch (component){
        case "orders":
            ShowComponent = Orders;
            break;
        case "stats":
            ShowComponent = Stats;
            break;
        default:
            ShowComponent = null;
            break;
    }

    const logOut = async () => {
        Cookies.remove('isLoggedIn');
        await axios.post("http://192.168.56.1:8000/api/validate/check/setLogIn",{
            status: false,
            email: cookieValue
        });
        navigate('/');
    };
    
    return (
    <div className='base'>
        <div className='leftSideMain'>
            <div style={{height: "75vh"}}>
                <div className='mainLogoBar'>
                    <img width = "100%" height = "100%" alt = "q" src = "/static/assets/video.gif"/>
                </div>
                <div className='mainText' onClick={changeToOrders}>Заказы</div>
                <div className='mainText' onClick={changeToStats}>Статистика</div>
            </div>
           <div style={{height: "25vh", display: "grid", alignItems: "end"}}>
                <div className="mainLogout" onClick={logOut}>Выйти</div>
           </div>
        </div>
        <div className='rightSideMain'>
            {<ShowComponent/>}
        </div>
    </div>
  );
};

export default Main;