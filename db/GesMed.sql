CREATE DATABASE GesMed;
USE GesMed;

-- tabla de medicos
CREATE TABLE Medicos (
    ID_Medico INT AUTO_INCREMENT PRIMARY KEY,
    RFC_Medico VARCHAR(13) UNIQUE,
    Nombre_Medico VARCHAR(40) NOT NULL,
    AP_Medico VARCHAR(40) NOT NULL,
    AM_Medico VARCHAR(40) NOT NULL,
    Cedula VARCHAR(20) NOT NULL,
    Correo_Medico VARCHAR(100) UNIQUE NOT NULL,
    Contrasena VARCHAR(60) NOT NULL,
    Rol ENUM('admin', 'medico'),
    Imagen_Medico LONGBLOB
);

-- Tabla para expedientes de pacientes
CREATE TABLE Pacientes (
    ID_Paciente INT AUTO_INCREMENT PRIMARY KEY,
    ID_Medico INT NOT NULL,               
	Nombre_Paciente VARCHAR(40) NOT NULL,
    AP_Paciente VARCHAR(40) NOT NULL,
    AM_Paciente VARCHAR(40) NOT NULL,
    FechaNacimiento DATE NOT NULL,
    EnfermedadesCronicas TEXT NOT NULL,    
    Alergias TEXT NOT NULL,                      
    AntecedentesFamiliares TEXT NOT NULL,     
    FOREIGN KEY (ID_Medico) REFERENCES Medicos(ID_Medico)
);

-- Tabla para citas y exploración/diagnóstico
CREATE TABLE Citas (
    ID_Cita INT AUTO_INCREMENT PRIMARY KEY,
    ID_Paciente INT NOT NULL,
    ID_Medico INT NOT NULL,
    Fecha DATE NOT NULL,
    Peso DECIMAL(5,2) NOT NULL,
    Altura DECIMAL(4,2) NOT NULL,
    Temperatura DECIMAL(4,2) NOT NULL,
    LatidosPorMinuto INT NOT NULL,
    SaturacionOxigeno DECIMAL(4,2) NOT NULL,
    Glucosa DECIMAL(5,2) NOT NULL,
    Sintomas TEXT NOT NULL,
    Diagnostico TEXT NOT NULL,
    Tratamiento TEXT NOT NULL,
    SolicitudEstudios TEXT,
    PDF_Receta LONGBLOB,
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_Medico) REFERENCES Medicos(ID_Medico)
);

-- Tabla para recetas (puede ser generado después de guardar cita)
CREATE TABLE Recetas (
    ID_Receta INT AUTO_INCREMENT PRIMARY KEY,
    ID_Cita INT NOT NULL,
    ID_Medico INT NOT NULL,
    FechaGeneracion DATE NOT NULL,
    FOREIGN KEY (ID_Cita) REFERENCES Citas(ID_Cita),
    FOREIGN KEY (ID_Medico) REFERENCES Medicos(ID_Medico)
);

SELECT * FROM Medicos;
SELECT * FROM Pacientes;
SELECT * FROM Citas;
SELECT * FROM Recetas;

-- INSERT
INSERT INTO Medicos (RFC_Medico, Nombre_Medico, AP_Medico, AM_Medico, Cedula, Correo_Medico, Contrasena, Rol, Imagen_Medico)
VALUES
('RAJR890101XXX', 'Rafael de Jesus', 'Reyes', 'Chavez', 'CED1234567', 'rafael.admin@example.com', 'ElMejorenBD', 'admin', NULL),
('MARU890202YYY', 'Maru', 'Hermosa', 'De Negocios', 'CED7654321', 'maru.medico@example.com', 'MeGustas', 'medico', NULL);
