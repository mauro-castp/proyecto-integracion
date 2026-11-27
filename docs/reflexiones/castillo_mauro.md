# Reflexión individual

**Mauro Castillo Peña · Matrícula 613512 · Equipo 04**  
Integración de Aplicaciones Computacionales · 27 de noviembre de 2026

## 1. Lo que hice

Durante el proyecto trabajé principalmente en las aplicaciones de escritorio y móvil. En la aplicación de escritorio agregué los módulos de Inventario, Preparación, Despacho y Surtido, junto con la asignación de pedidos a repartidores, la generación del manifiesto imprimible y el control de la interfaz para que los botones se habiliten según los permisos del usuario. En la app móvil construí la parte del cliente: el catálogo, el carrito, el flujo para hacer pedidos sin conexión, la vista de mis pedidos, la cancelación y la confirmación de recepción. Además, programé el tercer algoritmo de capacidad mediante el cálculo de colas M/M/c (`/capacidad/colas`), realicé pruebas contra la nube, aplicé la prueba de usabilidad con tres personas y empaqueté los instaladores para el Release.

## 2. Una decisión técnica que defendería

Defendería la implementación de pedidos sin conexión utilizando un `operacion_uuid`. Cuando el usuario pierde señal, el pedido se guarda en una cola local en el teléfono y se sincroniza automáticamente al recuperar internet. Como cada operación lleva un identificador único, el servidor garantiza idempotencia: aunque la petición se reintente o llegue duplicada por inestabilidad de la red, el pedido no se duplica. La alternativa más sencilla era bloquear la aplicación cuando no hubiera red, pero en un entorno móvil real eso habría afectado la experiencia del usuario y detenido la operación en campo.

## 3. Un problema difícil

Uno de los fallos más complicados fue el cierre inesperado de la aplicación móvil al abrir el lector de códigos QR. En el emulador el GPS funcionaba sin problemas, pero al abrir la cámara la app se cerraba de inmediato. Revisando el error vi que la librería del lector necesitaba una clase de `androidx.core` (`ContextCompat`) que no venía incluida en el APK. Lo resolví agregando esa dependencia y escribiendo una prueba que corre en el emulador (`elLectorDeQrAbreSinCerrarLaApp`) y comprueba que esa clase esté presente, para que el error no regrese en futuras compilaciones.

## 4. Lo que aprendí de integración

Aprendí que las aplicaciones cliente solo funcionan de manera estable cuando respetan al pie de la letra los contratos XML y JSON de cada microservicio. También comprobé que probar en un entorno local no es suficiente, ya que el despliegue en la nube con HTTPS introduce latencias, certificados y comportamientos distintos. Por último, diseñar para un modo sin conexión me enseñó que la integración distribuida obliga a anticipar duplicados y estados intermedios desde la arquitectura.

## 5. Lo que haría distinto

Haría la prueba de usabilidad mucho antes en el cronograma. Al hacerla al final descubrimos que en la app de escritorio resulta poco intuitivo llegar al PDF del reporte, y ya no tuvimos margen de tiempo para rediseñar ese flujo. También evitaría dejar el desarrollo y empaquetado de las aplicaciones cliente para la recta final, y conseguiría un teléfono Android físico desde la primera semana en lugar de depender tanto del emulador.

## 6. Mi aporte al trabajo en equipo

El equipo trabajó de manera muy equilibrada y cada quien asumió su parte. Me tocó encargarme de las pruebas de integración y de validar las aplicaciones, incluso en un momento en que Ruth no tenía conexión y tuvimos que avanzar por separado. Además, el trabajo colaborativo me dejó mucho aprendizaje: de Ruth aprendí sobre el despliegue en GCP y el manejo de la base de datos en la nube, mientras que de Majo aprendí cómo estructurar y comunicar mejor una presentación técnica.
