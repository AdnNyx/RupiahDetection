<template>
  <div class="min-h-screen bg-white p-6 md:p-12 font-sans text-gray-900">
    <div class="mx-auto max-w-7xl space-y-8">
      <div
        class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between border-b border-gray-200 pb-6"
      >
        <div>
          <h1 class="text-3xl font-semibold tracking-tight text-gray-900">
            Sistem Deteksi Rupiah
          </h1>
          <p class="mt-1 text-sm text-gray-500">
            Pemindai nominal uang kertas real-time dengan model YOLO
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <button
            @click="startCamera"
            :disabled="cameraActive"
            class="px-5 py-2.5 text-sm font-medium text-white bg-gray-900 border border-gray-900 rounded-md hover:bg-gray-800 disabled:bg-gray-100 disabled:text-gray-400 disabled:border-gray-200 disabled:cursor-not-allowed transition-colors"
          >
            Mulai Kamera
          </button>
          <button
            @click="stopCamera"
            :disabled="!cameraActive"
            class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Hentikan Kamera
          </button>
          <button
            @click="resetCount"
            class="px-5 py-2.5 text-sm font-medium text-gray-600 bg-gray-100 border border-transparent rounded-md hover:bg-gray-200 transition-colors"
          >
            Reset Data
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div
          class="relative flex w-full flex-col overflow-hidden rounded-lg border border-gray-200 bg-gray-50 lg:col-span-2 min-h-[400px] md:min-h-[500px]"
        >
          <div v-if="cameraActive" class="h-full w-full bg-black">
            <img
              :src="streamUrl"
              alt="Video Stream"
              class="h-full w-full object-contain"
            />
          </div>
          <div
            v-else
            class="flex h-full flex-col items-center justify-center text-gray-400"
          >
            <span
              class="text-sm font-medium uppercase tracking-widest text-gray-500"
            >
              Kamera Offline
            </span>
            <span class="mt-2 text-xs text-gray-400">
              Menunggu inisialisasi modul video...
            </span>
          </div>
        </div>

        <div class="flex flex-col gap-6">
          <div class="rounded-lg border border-gray-200 bg-white p-6">
            <h3
              class="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-500"
            >
              Total Terhitung
            </h3>
            <div class="text-4xl font-light tracking-tight text-gray-900">
              Rp {{ totalAmount.toLocaleString("id-ID") }}
            </div>
            <div
              class="mt-3 flex items-center justify-between border-t border-gray-100 pt-3 text-sm text-gray-500"
            >
              <span>Total lembar diproses</span>
              <span class="font-medium text-gray-900">{{ totalNotes }}</span>
            </div>
          </div>

          <div class="rounded-lg border border-gray-200 bg-white p-6 flex-1">
            <h3
              class="mb-4 border-b border-gray-100 pb-4 text-xs font-semibold uppercase tracking-wider text-gray-500"
            >
              Rincian Nominal
            </h3>

            <div
              v-if="Object.keys(details).length === 0"
              class="py-8 text-center text-sm text-gray-400"
            >
              Belum ada data terekam.
            </div>

            <ul v-else class="space-y-1">
              <li
                v-for="(count, nominal) in details"
                :key="nominal"
                class="flex items-center justify-between py-2"
              >
                <span class="text-sm text-gray-600">
                  Rp {{ parseInt(nominal).toLocaleString("id-ID") }}
                </span>
                <span class="text-sm font-medium text-gray-900">
                  {{ count }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from "vue";

const cameraActive = ref(false);
const streamUrl = ref("");
const totalAmount = ref(0);
const totalNotes = ref(0);
const details = ref({});
let intervalId = null;

const startCamera = () => {
  cameraActive.value = true;
  streamUrl.value =
    "http://127.0.0.1:8000/api/camera/stream?" + new Date().getTime();
  intervalId = setInterval(fetchSummary, 1000);
};

const stopCamera = async () => {
  try {
    await fetch("http://127.0.0.1:8000/api/camera/stop", { method: "POST" });
  } catch (e) {
    console.error("Gagal menghentikan kamera", e);
  }
  cameraActive.value = false;
  streamUrl.value = "";
  if (intervalId) clearInterval(intervalId);
};

const resetCount = async () => {
  try {
    await fetch("http://127.0.0.1:8000/api/count/reset", { method: "POST" });
    await fetchSummary();
  } catch (e) {
    console.error("Gagal mereset", e);
  }
};

const fetchSummary = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/count-summary");
    const data = await res.json();
    totalAmount.value = data.summary.total_amount;
    totalNotes.value = data.summary.total_notes;

    const filteredDetails = {};
    for (const [nom, count] of Object.entries(data.summary.details)) {
      if (count > 0) filteredDetails[nom] = count;
    }
    details.value = filteredDetails;
  } catch (e) {
    console.error("Gagal mengambil data", e);
  }
};

onUnmounted(() => stopCamera());
</script>
