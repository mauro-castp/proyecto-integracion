# Microhubs · cliente de escritorio (parte B)

Aplicación C# / Windows Forms para planeador, administrador y auditor. Solo intercambia XML con namespace `urn:microhubs:v1`; valida las respuestas no vacías con XSD y rechaza DTD. Los auditores pueden consultar/exportar, pero no modificar ni simular.

## Ejecutar

Requiere Windows y **SDK .NET 8** (el runtime no basta):

```powershell
cd app_escritorio
dotnet run
```

El modo «Ejemplos locales» está marcado inicialmente. Usa cualquier correo válido y clave no vacía. Los candidatos creados/modificados se guardan solo en memoria. Consulta candidatos, selecciona uno y simula; consulta pedidos cerrados, aplica búsqueda y filtro, y exporta XML. El login de ejemplo no autentica contra ningún servidor.

Para servicios reales desmarca el modo local y configura un host HTTPS con certificado confiable. Los puertos son 5101 (auth), 5103 (catálogos), 5104 (pedidos), 5106 (planeación). No se omiten errores TLS. Los tokens viven solo en memoria y se eliminan al salir, incluso si el servidor no responde. La expiración/formato del JWT se comprueba localmente; **la firma, sesión y revocación deben validarlas los servicios**, sin distribuir el secreto HS256 al cliente. La renovación automática se intenta una vez ante 401.

## Contrato provisional: pendiente de acordar con parte A

`contratos/cliente.xsd` y los ejemplos son propuestas del cliente, no contratos v1 congelados. Reemplazarlos por los XSD oficiales al publicarse. El esquema exige la estructura y tipos; campos adicionales actualmente se rechazan, deliberadamente.

- POST `auth/login`: `<login><correo/><clave/></login>` → `sesion.xml`.
- POST `auth/renovar`: `<renovar><token_renovacion/></renovar>` → misma sesión completa.
- POST `auth/salir`: `<salir><token_renovacion/></salir>` → 204 o `<resultado><mensaje/></resultado>`.
- GET `productos`, GET `pedidos?estado=entregado`, GET `candidatos` → `lista.xml` (producto/pedido/candidato).
- POST `candidatos`, PUT `candidatos/{id}`: `<candidato><nombre/></candidato>` → resultado.
- POST `candidatos/{id}/simular`: `<simular/>` → `simulacion.xml`.

Todos los cuerpos anteriores llevan el namespace. `Accept` y `Content-Type` son `application/xml`. La consulta muestra la primera página que devuelve el servicio; la exportación contiene esa respuesta, no toda la base de datos. El filtro se aplica a esa página.

## Verificación

```powershell
python -m pip install lxml
python -m unittest discover -s pruebas -v
dotnet build
```

Pruebas de esquema: ejemplos válidos, sesión incompleta, namespace incorrecto, ID negativo y booleano inválido. Se verificaron la compilación, la inicialización de Windows Forms y 17 comprobaciones de flujo/protocolo. Se instaló un SDK local en `.tools/dotnet/` y se generó una publicación autónoma en `bin/Publicacion/Microhubs.exe`. La comunicación real queda pendiente de los servicios/contratos compartidos. Ver `PRUEBAS_APPS.md`.

## Ensayo manual

1. Entrar en ejemplos; listar candidatos, crear uno y modificarlo por ID; volver a listar.
2. Simular un candidato seleccionado; verificar búsqueda, filtro y exportación XML.
3. Salir: tabla y sesión deben quedar vacías.
4. Con backend: probar contraseña incorrecta, 401 con renovación, 403, respuesta XML inválida, desconexión y revocación.
