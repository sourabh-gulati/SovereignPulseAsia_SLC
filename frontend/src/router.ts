import { createRouter, createWebHistory } from 'vue-router'
import YieldCurveView from './views/YieldCurveView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: YieldCurveView }
  ]
})
