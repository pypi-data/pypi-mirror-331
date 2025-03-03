# 📌 SQLitePlus-Enhanced - Base de Datos Mejorada con Cifrado y Caché 🚀

## 📖 Descripción
`sqliteplus-enhanced` es una librería que extiende SQLite con características avanzadas:
- **Cifrado con SQLCipher** 🔒
- **Caché en Redis** para mejorar el rendimiento ⚡
- **Manejo de concurrencia con threading** 🛠️
- **Exportación y replicación de datos** 📂
- **Interfaz CLI para administración desde la terminal** 🖥️
- **Servidor API con FastAPI** para integración flexible 🌐

---

## 📦 Instalación
Puedes instalar la librería directamente desde PyPI con:
```bash
pip install sqliteplus-enhanced
```

---

## 🚀 Uso

### **🔹 Inicializar la Base de Datos**
```bash
sqliteplus-enhanced init-db
```

### **🔹 Ejecutar una Consulta de Escritura**
```bash
sqliteplus-enhanced execute "INSERT INTO logs (action) VALUES ('Test desde CLI')"
```

### **🔹 Ejecutar una Consulta de Lectura**
```bash
sqliteplus-enhanced fetch "SELECT * FROM logs"
```

### **🔹 Crear una Copia de Seguridad**
```bash
sqliteplus-enhanced backup
```

### **🔹 Exportar una Tabla a CSV**
```bash
sqliteplus-enhanced export-csv logs logs_export.csv
```

---

## ⚙️ Configuración de Redis (Opcional pero Recomendado)
Si deseas habilitar la caché en Redis:
1. **Iniciar Redis en Local**
   ```bash
   redis-server
   ```
2. **Verificar que Redis está activo**
   ```bash
   redis-cli ping  # Debería responder con 'PONG'
   ```

---

## 📡 Uso del Servidor API
### **🔹 Iniciar el Servidor FastAPI**
```bash
uvicorn sqliteplus.server:app --reload --host 0.0.0.0 --port 8000
```

### **🔹 Acceder a la Documentación Interactiva**
Abre en tu navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📜 Licencia
Este proyecto está bajo la licencia **MIT**.

---

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si deseas mejorar `sqliteplus-enhanced`, puedes abrir un issue en GitHub.

---

## 📧 Contacto
Si tienes dudas o sugerencias, puedes contactarme en **[tuemail@example.com](mailto:tuemail@example.com)**.
