import React, {useState, useEffect} from 'react';
import './css/orders.css';
//import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
//<div style={{width: "100%", height:"100vh", backgroundColor:"black"}}></div>

const Orders = () => {
  let [newOrders, setOrders] = useState([]);  
  let [company, setCompany] = useState("");
  const getOrders = async () =>{
    try{
      let resp = await axios.post('http://192.168.56.1:8000/api/getOrders', {
        company: company,
      });
      setOrders(resp.data.orders);
    } catch (error){
    }
  };

  const updateOrder = async (order_id) => {
    try{
      await axios.post('http://192.168.56.1:8000/api/orderComplete', {
        order_id: order_id,
      });
    }
    catch{
    }
  }
  
  useEffect(() => {
    setCompany(Cookies.get('company_id'));
    const interval = setInterval(getOrders, 1000);
    return () => clearInterval(interval);
  }, [getOrders, company]);

    return (
      <div className='orderMainBlock'>
        <div className='orderTopBlock'>
          <div className='orderTopBlockDescription'>order id</div>
          <div className='orderTopBlockDescription'>tg name</div>
          <div className='orderTopBlockDescription'>order details</div>
          <div className='orderTopBlockDescription'>status</div>
        </div>
        <div className='orderBotBlock'>
          {newOrders.map((order) => (
            <div key={order.order_id} className='orderDisplay'>
              <div className='orderDisplayInside'>{order.order_id}</div>
              <div className='orderDisplayInside'>{order.customer_telegram_id.tg_name}</div>
              <div className='orderDisplayInside'>{order.order_details}</div>
              <div className='orderDisplayInside'>
                <button onClick={() => updateOrder(order.order_id)}>
                  Выполнен
                </button>
              </div>
            </div> 
          ))}
        </div>
      </div>
    );
};

export default Orders;