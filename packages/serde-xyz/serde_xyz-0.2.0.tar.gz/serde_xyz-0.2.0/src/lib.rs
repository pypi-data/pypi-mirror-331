use pyo3::prelude::*;
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::fmt;

#[pyclass]
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Atom {
    #[pyo3(get, set)]
    pub element: String,
    #[pyo3(get, set)]
    pub x: f64,
    #[pyo3(get, set)]
    pub y: f64,
    #[pyo3(get, set)]
    pub z: f64,
}

#[pymethods]
impl Atom {
    #[new]
    pub fn new(element: String, x: f64, y: f64, z: f64) -> Self {
        Self { element, x, y, z }
    }
}

/// Class representing a molecular structure .xyz file.
///
/// ```py
/// from serde_xyz import Atom, XYZ
///
/// atoms = [
///     Atom("O", 0, 0, 0),
///     Atom("H", 1, 0, 0),
///     Atom("H", 0, 1, 0),
/// ]
///
/// xyz = XYZ(atoms, "this is a comment")
///
/// print(xyz.to_string())
///
/// xyz2 = XYZ.from_string("3\nthis is a comment\nO 0 0 0\nH 1 0 0\n H 0 1 0")
/// ```
#[pyclass]
#[derive(Debug, Clone, PartialEq)]
pub struct XYZ {
    pub atoms: Vec<Atom>,
    pub comment: String,
}

#[pymethods]
impl XYZ {
    #[new]
    pub fn new(atoms: Vec<Atom>, comment: String) -> Self {
        Self { atoms, comment }
    }

    pub fn __str__(&self) -> PyResult<String> {
        Ok(self.to_string()?)
    }

    pub fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "XYZ(atoms={:?}, comment='{}')",
            self.atoms, self.comment
        ))
    }

    pub fn to_string(&self) -> PyResult<String> {
        let serialized = serde_json::to_string(&self)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(serialized)
    }

    #[staticmethod]
    pub fn from_string(s: &str) -> PyResult<Self> {
        let xyz: XYZ = serde_json::from_str(s)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(xyz)
    }
}

impl Serialize for XYZ {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut output = format!("{}\n{}\n", self.atoms.len(), self.comment);
        for atom in &self.atoms {
            output.push_str(&format!(
                "{} {:.6} {:.6} {:.6}\n",
                atom.element, atom.x, atom.y, atom.z
            ));
        }
        serializer.serialize_str(&output)
    }
}

impl<'de> Deserialize<'de> for XYZ {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let s: String = Deserialize::deserialize(deserializer)?;
        let mut lines = s.lines();

        let atom_count: usize = lines
            .next()
            .ok_or_else(|| serde::de::Error::custom("Missing atom count"))?
            .parse()
            .map_err(|_| serde::de::Error::custom("Invalid atom count"))?;

        let comment = lines
            .next()
            .ok_or_else(|| serde::de::Error::custom("Missing comment"))?
            .to_string();

        let mut atoms = Vec::new();
        for line in lines.take(atom_count) {
            let mut parts = line.split_whitespace();
            let element = parts
                .next()
                .ok_or_else(|| serde::de::Error::custom("Missing element"))?
                .to_string();
            let x: f64 = parts
                .next()
                .ok_or_else(|| serde::de::Error::custom("Missing x coordinate"))?
                .parse()
                .map_err(|_| serde::de::Error::custom("Invalid x coordinate"))?;
            let y: f64 = parts
                .next()
                .ok_or_else(|| serde::de::Error::custom("Missing y coordinate"))?
                .parse()
                .map_err(|_| serde::de::Error::custom("Invalid y coordinate"))?;
            let z: f64 = parts
                .next()
                .ok_or_else(|| serde::de::Error::custom("Missing z coordinate"))?
                .parse()
                .map_err(|_| serde::de::Error::custom("Invalid z coordinate"))?;

            atoms.push(Atom { element, x, y, z });
        }

        if atoms.len() != atom_count {
            return Err(serde::de::Error::custom("Atom count mismatch"));
        }

        Ok(XYZ { atoms, comment })
    }
}

impl fmt::Display for XYZ {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "{}", self.atoms.len())?;
        writeln!(f, "{}", self.comment)?;
        for atom in &self.atoms {
            writeln!(
                f,
                "{} {:.6} {:.6} {:.6}",
                atom.element, atom.x, atom.y, atom.z
            )?;
        }
        Ok(())
    }
}

/// Serialize and deserialize molecular structure .xyz files.
///
/// ```py
/// from serde_xyz import Atom, XYZ
///
/// atoms = [
///     Atom("O", 0, 0, 0),
///     Atom("H", 1, 0, 0),
///     Atom("H", 0, 1, 0),
/// ]
///
/// xyz = XYZ(atoms, "this is a comment")
///
/// xyz
/// >>> XYZ(atoms=[
///            Atom { element: "O", x: 0.0, y: 0.0, z: 0.0 },
///            Atom { element: "H", x: 1.0, y: 0.0, z: 0.0 },
///            Atom { element: "H", x: 0.0, y: 1.0, z: 0.0 }
///         ],
///         comment='this is a commment'
///     )
///
/// print(xyz)
/// >>> "3\n\nO 0.000000 0.000000 0.000000\nH 1.000000 0.000000 0.000000\nH 0.000000 1.000000 0.000000\n"
///
/// str(xyz)
/// >>> '"3\\n\\nO 0.000000 0.000000 0.000000\\nH 1.000000 0.000000 0.000000\\nH 0.000000 1.000000 0.000000\\n"'
/// ```
#[pymodule]
fn serde_xyz(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Atom>()?;
    m.add_class::<XYZ>()?;
    Ok(())
}
