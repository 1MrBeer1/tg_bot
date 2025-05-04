import React, { useState, useEffect } from 'react';
import Notification from './Notification';
import './css/logInPage.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';

function LogInPage(){
    const [showNotification, setShowNotification] = useState(false);
    const [errorMessage, setMessage] = useState("anError");
    const [newEmail, setEmail] = useState("");
    const [password, setPassword] = useState("");   
    const navigate = useNavigate();
    const cookieValue = Cookies.get('isLoggedIn');

    useEffect(() => {
        let resp;
        const sendCheck = async () =>{
            resp = await axios.post("http://192.168.56.1:8000/api/validate/check/isLoggedIn",{
                email: cookieValue
            });
            if(resp.status === 200) navigate('/main');
        }
        
        if (cookieValue !== undefined) {
            sendCheck();
        }
    }, [cookieValue, navigate]);

    const handleShowNotification = () => {
        setShowNotification(true);
    };
    
    const handleCloseNotification = () => {
        setShowNotification(false);
    };

    const handleEmailChange = (event) => {
        setEmail(event.target.value);
    };

    const handlePassChange = (event) => {
        setPassword(event.target.value);
    };

    const validateLogIn = async () => {
        try{
            const res = await axios.post("http://192.168.56.1:8000/api/validate/check/logIn",{
                email: newEmail,
                pass : password
            });
            switch(res.status){
                case 200:
                    Cookies.set('isLoggedIn', newEmail, { expires: 1 });
                    let answ = await axios.post("http://192.168.56.1:8000/api/validate/check/setLogIn",{
                        status: true,
                        email: newEmail,
                    });
                    Cookies.set('company_id', answ.data.company_id, { expires: 1 });
                    navigate('/main');
                    break;
                case 203:
                    Cookies.remove('isLoggedIn');
                    setMessage("Authorization error");
                    handleShowNotification();
                    break;
                case 204:
                    Cookies.remove('isLoggedIn');
                    setMessage("Not found");
                    handleShowNotification();
                    break;
                default:
                    Cookies.remove('isLoggedIn');
                    setMessage("Unexpected error");
                    handleShowNotification();
                    break;
            }
        }
        catch(error){
            setMessage("POST error");
            handleShowNotification();
            //console.error("an error: ", error)
        }
    };

    return(
        <div
            className='main'>
            <div
                className='main_block'>
                    <div>
                        Вход
                    </div>
                    <input 
                        type="email"
                        className='input_box'
                        onChange={handleEmailChange}/>
                    <input 
                        type="password"
                        className='input_box'
                        onChange={handlePassChange}/>
                    <input 
                        type="button"
                        className='submit_button'
                        value="Войти"
                        onClick={validateLogIn}/>
            </div>
            <Notification
                message = {errorMessage}
                show={showNotification}
                onClose={handleCloseNotification}
            />
        </div>
    );
}

export default LogInPage;