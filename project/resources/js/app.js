import { createApp } from 'vue';
import { createPinia } from 'pinia';
import 'bootstrap/dist/css/bootstrap.min.css';
import App from './App.vue';
const element = document.querySelector('#app');
createApp(App, { advanced: element.dataset.advanced === 'true' }).use(createPinia()).mount(element);
