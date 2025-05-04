import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

const Protector = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const cookieValue = Cookies.get('isLoggedIn');
    console.log(cookieValue);
    if (cookieValue === undefined) {
      navigate('/');
    } else {
      navigate('/main');
    }
  }, [navigate]);

  return null;
};

export default Protector;