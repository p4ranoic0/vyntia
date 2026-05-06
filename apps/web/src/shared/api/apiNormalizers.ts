type UnknownRecord = Record<string, unknown>;

const asRecord = (value: unknown): UnknownRecord =>
  value && typeof value === "object" ? (value as UnknownRecord) : {};

const asArray = (value: unknown): unknown[] =>
  Array.isArray(value) ? value : [];

const getString = (value: unknown, fallback = ""): string =>
  typeof value === "string" ? value : fallback;

const getNumber = (value: unknown, fallback = 0): number =>
  typeof value === "number" ? value : fallback;

export const extractCollection = (raw: unknown): unknown[] => {
  const rawObj = asRecord(raw);
  const data =
    asRecord(rawObj.data).results ?? rawObj.results ?? rawObj.data ?? raw;

  return asArray(data);
};

export const normalizeRole = (role: unknown) => {
  const roleObj = asRecord(role);
  const roleId = getString(roleObj.rol_id ?? roleObj.id);
  const isActive = roleObj.is_active === true;
  const estadoRol = getString(
    roleObj.estado_rol,
    isActive ? "activo" : "inactivo",
  );

  return {
    id: roleId,
    nombre_rol: getString(roleObj.nombre_rol ?? roleObj.nombre),
    descripcion_rol: getString(roleObj.descripcion_rol ?? roleObj.descripcion),
    estado_rol: estadoRol,
    is_active: estadoRol === "activo",
    total_usuarios: getNumber(roleObj.total_usuarios ?? roleObj.users_count),
    total_permisos: getNumber(
      roleObj.total_permisos ?? roleObj.permissions_count,
    ),
    permisos: asArray(roleObj.permisos),
  };
};

export const normalizeSecurityRole = (role: unknown) => {
  const normalized = normalizeRole(role);

  return {
    id: normalized.id,
    nombre: normalized.nombre_rol,
    descripcion: normalized.descripcion_rol,
    is_active: normalized.is_active,
    permissions_count: normalized.total_permisos,
    users_count: normalized.total_usuarios,
    permisos: normalized.permisos,
  };
};

export const normalizeUser = (user: unknown) => {
  const userObj = asRecord(user);
  const userId = getString(userObj.usuario_id ?? userObj.id);
  const isActive = userObj.is_active === true;
  const estadoUsuario = getString(
    userObj.estado_usuario,
    isActive ? "activo" : "inactivo",
  );

  return {
    id: userId,
    username: getString(userObj.username ?? userObj.nombre_usuario),
    email: getString(userObj.email ?? userObj.correo_institucional),
    nombres_usuario: getString(userObj.nombres_usuario),
    apellidos_usuario: getString(userObj.apellidos_usuario),
    tipo_usuario: getString(userObj.tipo_usuario),
    nivel_acceso: getString(userObj.nivel_acceso),
    estado_usuario: estadoUsuario,
    is_active: estadoUsuario === "activo",
    date_joined: userObj.date_joined ?? userObj.created_at ?? null,
    last_login: userObj.last_login ?? userObj.ultimo_acceso ?? null,
    empleado: userObj.empleado_detalle ?? userObj.empleado,
    roles_activos: asArray(userObj.roles_activos).map((role) =>
      normalizeRole(role),
    ),
    dias_sin_login: userObj.dias_sin_login,
    ultimo_login_texto: userObj.ultimo_login_texto,
  };
};

export const normalizeEmployee = (employee: unknown) => {
  const employeeObj = asRecord(employee);
  const ubicacionActual = asRecord(employeeObj.ubicacion_actual);
  const employeeId = getString(employeeObj.empleado_id ?? employeeObj.id);

  return {
    id: employeeId,
    nombres: getString(employeeObj.nombres_empleado ?? employeeObj.nombres),
    ape_paterno: getString(
      employeeObj.apellido_paterno ?? employeeObj.ape_paterno,
    ),
    ape_materno: getString(
      employeeObj.apellido_materno ?? employeeObj.ape_materno,
    ),
    dni: getString(employeeObj.numero_documento ?? employeeObj.dni),
    telefono: getString(employeeObj.telefono_celular ?? employeeObj.telefono),
    email: getString(employeeObj.correo_personal ?? employeeObj.email),
    fecha_nacimiento: employeeObj.fecha_nacimiento,
    direccion: employeeObj.direccion_domicilio ?? employeeObj.direccion,
    estado_civil: employeeObj.estado_civil,
    genero: employeeObj.genero_empleado ?? employeeObj.genero,
    area:
      employeeObj.area ??
      (Object.keys(ubicacionActual).length > 0
        ? {
            id: getString(ubicacionActual.area_id),
            organo: getString(ubicacionActual.area_nombre),
            siglas: getString(ubicacionActual.area_siglas),
          }
        : undefined),
    cargo: employeeObj.cargo,
    fecha_ingreso: employeeObj.fecha_ingreso,
    estado: employeeObj.estado_empleado ?? employeeObj.estado,
    usuario: employeeObj.usuario,
  };
};
