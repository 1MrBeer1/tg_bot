import { makeAutoObservable } from "mobx";

class Store {
  isLogged = false;

  constructor() {
    makeAutoObservable(this);
  }

  setLogged() {
    this.isLogged = true;
  }

  setUnLogged() {
    this.isLogged = false;
  }
}

const store = new Store();
export default store;