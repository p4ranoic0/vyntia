// Inicializar MSW solo en entorno de desarrollo
async function setupMSW() {
  if (process.env.NODE_ENV === 'development') {
    const { worker } = await import('./browser');
    await worker.start({
      onUnhandledRequest: 'bypass', // No mostrar advertencias para peticiones no interceptadas
    });
    
    console.log('%cMock Service Worker activado', 'color: orange; font-weight: bold;');
  }
}

setupMSW().catch(error => {
  console.error('Error al inicializar Mock Service Worker:', error);
});