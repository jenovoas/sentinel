# Spec Delta

## Purpose

Define el aprovisionamiento seguro y reversible de cargas de cómputo Docker por tenant, con controles observables de aislamiento y capacidad antes de crear recursos.

## ADDED Requirements

### Requirement: El aprovisionamiento debe estar autorizado y acotado al tenant
El ejecutor MUST aceptar solo solicitudes autenticadas con un tenant autorizado y un identificador de solicitud idempotente. MUST limitar cada operación a los recursos declarados para esa solicitud.

#### Scenario: Solicitud autenticada y repetida
- **WHEN** llega de nuevo una solicitud válida con el mismo tenant e identificador idempotente
- **THEN** el ejecutor devuelve la operación existente sin crear recursos duplicados

#### Scenario: Solicitud no autorizada
- **WHEN** la autenticación falla o el tenant no está autorizado
- **THEN** el ejecutor rechaza la solicitud sin crear ni modificar recursos

### Requirement: El almacenamiento debe respetar una cuota dura por tenant
El ejecutor MUST verificar que el almacenamiento persistente limita físicamente el consumo de cada tenant y MUST detener la operación si no puede demostrar el límite solicitado.

#### Scenario: Host sin cuota dura demostrable
- **WHEN** la ruta de almacenamiento no informa un límite duro verificable igual o menor al solicitado
- **THEN** el ejecutor bloquea el aprovisionamiento y no afirma que la cuota esté aplicada

#### Scenario: Tenant alcanza su límite
- **WHEN** los datos persistentes del tenant consumen su capacidad máxima
- **THEN** nuevas escrituras excedentes fallan sin consumir la cuota asignada a otro tenant

### Requirement: Los artefactos de almacenamiento deben ser seguros e íntegros
La imagen ext4 MUST pertenecer al usuario efectivo del aprovisionador, no ser accesible por grupo u otros y conservar su asignación física completa después de formatearse. La unidad systemd MUST ser un archivo regular seguro y coincidir exactamente con la configuración esperada. El aprovisionador MUST rechazar archivos existentes inseguros o incompatibles sin modificarlos.

#### Scenario: Imagen o unidad existente insegura
- **WHEN** la imagen tiene permisos accesibles por grupo u otros, o la unidad no es regular, segura y coincidente
- **THEN** el aprovisionador se detiene antes de solicitar el montaje y conserva los archivos existentes

#### Scenario: Formateo reduce la asignación física
- **WHEN** la imagen ext4 no conserva bloques asignados por todo su tamaño después del formato
- **THEN** el aprovisionador no publica la imagen ni instala la unidad systemd

### Requirement: Los recursos deben estar aislados y sin exposición pública
Cada carga MUST usar una red dedicada a su tenant y MUST carecer de puertos publicados públicamente. El sistema MUST impedir que un tenant alcance recursos de red de otro tenant.

#### Scenario: Tráfico entre tenants
- **WHEN** una carga intenta conectar con una dirección de la red privada de otro tenant
- **THEN** la conexión es denegada

#### Scenario: Inspección de exposición
- **WHEN** se verifica una carga aprovisionada
- **THEN** no existe listener público ni mapeo de puerto hacia la carga

### Requirement: Los límites de CPU y memoria deben ser efectivos
Cada carga MUST aplicar límites de CPU y memoria no superiores a los valores autorizados para su solicitud.

#### Scenario: Carga supera su límite
- **WHEN** la carga intenta consumir CPU o memoria por encima de los valores asignados
- **THEN** el runtime aplica el límite y mantiene intactos los valores asignados a otras cargas

### Requirement: La operación debe poder destruir solo sus propios recursos
El ejecutor MUST conservar la relación entre la solicitud y sus recursos, y MUST eliminar únicamente los recursos propiedad de esa operación cuando se autoriza su destrucción.

#### Scenario: Destrucción de una carga
- **WHEN** se autoriza destruir una solicitud existente
- **THEN** se eliminan su contenedor, red y almacenamiento asociado sin afectar recursos de otros tenants

### Requirement: El estado remoto debe persistir y bloquear operaciones concurrentes
El ejecutor MUST usar un backend remoto con persistencia y lock funcional. MUST fallar cerrado si el backend no está configurado o el lock no puede adquirirse, y MUST NOT usar estado local como alternativa operativa.

#### Scenario: Backend o lock no disponible
- **WHEN** una operación no puede inicializar el backend remoto o adquirir el lock
- **THEN** no ejecuta Terraform y conserva un estado de operación saneado

### Requirement: El catálogo de cargas debe ser cerrado
El ejecutor MUST rechazar imágenes y operaciones que no estén explícitamente aprobadas. Cada imagen admitida MUST tener digest inmutable revisado y sus `VOLUME` y rutas escribibles deben asignarse a almacenamiento limitado.

#### Scenario: Plantilla no seleccionada
- **WHEN** no existe plantilla aprobada para la solicitud
- **THEN** el ejecutor rechaza el despliegue sin elegir una carga por inferencia

### Requirement: Preflight y daemon Docker deben compartir host
La comprobación de almacenamiento y la ruta bind MUST referirse al mismo host que ejecuta el daemon Docker. El sistema MUST NOT afirmar una cuota verificada cuando el proveedor Docker es remoto respecto del host inspeccionado.

#### Scenario: Preflight en host diferente
- **WHEN** el daemon Docker usa un host distinto del host inspeccionado
- **THEN** la operación queda bloqueada antes de crear recursos

### Requirement: La operación debe fallar de forma segura ante precondiciones incompletas
El ejecutor MUST bloquear la creación si falta una precondición de seguridad o capacidad y MUST exponer un estado saneado que identifique el tipo de bloqueo sin revelar secretos ni detalles internos.

#### Scenario: Falta identidad piloto
- **WHEN** no existe una identidad tenant autorizada para la solicitud
- **THEN** la operación queda bloqueada y no se crean recursos

#### Scenario: Estado de cuota no comprobable
- **WHEN** el host no permite verificar el almacenamiento o los límites efectivos
- **THEN** el estado queda bloqueado y no se informa la carga como disponible
