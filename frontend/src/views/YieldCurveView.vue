<script setup lang="ts">
import { ref } from 'vue'
import SovereignYieldChart from '../components/SovereignYieldChart.vue'
import type { SovereignTenor } from '../services/api'
import indiaFlag from '../assets/flags/india.svg'
import japanFlag from '../assets/flags/japan.svg'
import taiwanFlag from '../assets/flags/taiwan.svg'

const selectedMarket = ref('india')
const standardTenors: SovereignTenor[] = ['1Y', '2Y', '5Y', '10Y']
const taiwanTenors: SovereignTenor[] = ['2Y', '5Y', '10Y']
function jumpToMarket() { document.getElementById(selectedMarket.value)?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
</script>

<template><main class="yield-page"><nav class="topbar"><a class="brand" href="/">Sovereign Pulse Asia<span>_SLC</span></a><label class="market-select"><span>Market</span><select v-model="selectedMarket" aria-label="Jump to a government bond market" @change="jumpToMarket"><option value="india">India</option><option value="japan">Japan</option><option value="taiwan">Taiwan</option></select></label></nav><SovereignYieldChart id="india" market="India" :flag-src="indiaFlag" description="Monthly month-end yield history for India’s sovereign debt market." history-path="/india-gsec/history" latest-label="LATEST MONTH-END YIELD" change-label="Change across available history" :tenors="standardTenors"/><SovereignYieldChart id="japan" market="Japan" :flag-src="japanFlag" description="Daily constant-maturity yield history for Japan’s sovereign debt market." history-path="/japan-gsec/history" latest-label="LATEST DAILY YIELD" change-label="1-year change" :tenors="standardTenors"/><SovereignYieldChart id="taiwan" market="Taiwan" :flag-src="taiwanFlag" description="Daily benchmark yield history for Taiwan’s sovereign debt market." history-path="/taiwan-gsec/history" latest-label="LATEST BENCHMARK YIELD" change-label="Change across available history" :tenors="taiwanTenors"/></main></template>
