# Reflexión individual sobre el proyecto Microhubs

**Vanessa Morante López · Matrícula 654008 · Equipo 04**  
Integración de Aplicaciones Computacionales · 27 de noviembre de 2026

El proyecto de Microhubs me pareció interesante porque partió de una pregunta que podía aplicarse a un caso real: ¿dónde conviene instalar un microhub en San Bernabé y qué tendría que pasar para que valga la pena operarlo? Al principio me parecía que bastaba con elegir un punto cercano a los clientes. Conforme avanzamos, entendí que una ubicación puede cubrir muchos hogares y aun así quedarse corta si el microhub no tiene capacidad para atender la demanda o si los pedidos no generan suficiente margen para pagar la operación. Me gustó que la plataforma nos permitiera comparar esos factores y explicar de dónde sale una recomendación.

## Mi aportación al equipo

Participé de forma importante en el diseño de la base de datos. Hice el modelo entidad-relación, trabajé la normalización y llevé ese diseño al modelo físico de PostgreSQL. En el modelo tuve que representar cómo se relacionan los pedidos, los productos, el inventario y los microhubs. Ese trabajo empezó con las reglas del negocio y terminó en decisiones concretas sobre qué datos guardar, cómo relacionarlos y qué restricciones aplicar para evitar inconsistencias. También apoyé en la revisión de los módulos CRUD, especialmente al decidir en qué partes tenía sentido permitir altas, cambios y bajas, y en cuáles era mejor seguir un proceso con reglas propias, como la cancelación de un pedido.

Una decisión de diseño que defendería es separar el catálogo de productos del inventario de cada microhub. Un producto puede venderse en varios puntos y tener una cantidad disponible distinta en cada uno. Si copiáramos todos sus datos en cada registro de inventario, un cambio en la descripción tendría que hacerse varias veces. Con el diseño relacional, el equipo puede consultar la disponibilidad por ubicación y actualizar los datos del producto desde el catálogo. Me gustó ver que algo que habíamos dibujado en el modelo terminaba siendo necesario para decidir desde dónde surtir un pedido.

## Lo que aprendí y qué haría diferente

Una de las cosas que más me hizo pensar fue el problema de las cancelaciones que encontró el equipo durante las pruebas. Se actualizaba el estado del pedido directamente y las existencias quedaban descontadas. Para corregirlo, se repuso el inventario y se ajustaron las pruebas para usar la función que devuelve las unidades. Al revisar ese caso, me quedó claro que para comprobar que una cancelación funciona hay que revisar tanto lo que ve la persona en pantalla como lo que queda guardado en la base de datos.

También me pareció valioso ver cómo las aportaciones del equipo se conectaron. Un pedido que se confirma en la web tiene que aparecer en la operación del microhub y, una vez asignado, estar disponible para el repartidor en Android. En ese punto se entiende por qué importan los contratos de las API y por qué los servicios tienen que acordar qué significa cada estado. La parte que más dominaba era el diseño de datos, y trabajar con mis compañeros me ayudó a entender lo que necesitan las aplicaciones, las pruebas y el despliegue para funcionar con ese diseño.

Si volviera a hacer el proyecto, acordaría desde el primer parcial una prueba que siga un pedido completo y otra que revise qué pasa cuando se cancela o falla un paso. También anotaría junto a cada cambio de la base qué servicio y qué pantallas dependen de él. Eso nos habría facilitado revisar el impacto de los cambios antes de reunir todo para la entrega. Terminé satisfecha con mi aportación porque pude llevar el diseño desde el modelo hasta una estructura que el equipo podía usar para operar los microhubs y evaluar si conviene abrirlos.
