"""Ejemplo de recomendación de productos usando K vecinos más cercanos."""

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# Cada fila representa un producto; la categoría será la etiqueta que aprenderá el modelo.
products = pd.DataFrame(
	[
		{"producto": "Ratón inalámbrico", "precio": 29.99, "valoracion": 4.4, "popularidad": 80, "categoria": "Accesorios"},
		{"producto": "Teclado mecánico", "precio": 79.99, "valoracion": 4.7, "popularidad": 90, "categoria": "Accesorios"},
		{"producto": "Webcam HD", "precio": 49.99, "valoracion": 4.2, "popularidad": 70, "categoria": "Accesorios"},
		{"producto": "Hub USB-C", "precio": 24.99, "valoracion": 4.1, "popularidad": 65, "categoria": "Accesorios"},
		{"producto": "Soporte portátil", "precio": 34.99, "valoracion": 4.3, "popularidad": 75, "categoria": "Accesorios"},
		{"producto": "Auriculares Bluetooth", "precio": 59.99, "valoracion": 4.6, "popularidad": 88, "categoria": "Audio"},
		{"producto": "Altavoz inteligente", "precio": 89.99, "valoracion": 4.5, "popularidad": 82, "categoria": "Audio"},
		{"producto": "Auriculares de estudio", "precio": 129.99, "valoracion": 4.8, "popularidad": 72, "categoria": "Audio"},
		{"producto": "Barra de sonido", "precio": 149.99, "valoracion": 4.4, "popularidad": 78, "categoria": "Audio"},
		{"producto": "Micrófono USB", "precio": 69.99, "valoracion": 4.5, "popularidad": 74, "categoria": "Audio"},
		{"producto": "Lámpara de escritorio", "precio": 39.99, "valoracion": 4.3, "popularidad": 68, "categoria": "Hogar"},
		{"producto": "Cafetera", "precio": 99.99, "valoracion": 4.6, "popularidad": 85, "categoria": "Hogar"},
		{"producto": "Purificador de aire", "precio": 179.99, "valoracion": 4.4, "popularidad": 73, "categoria": "Hogar"},
		{"producto": "Aspiradora", "precio": 229.99, "valoracion": 4.7, "popularidad": 89, "categoria": "Hogar"},
		{"producto": "Báscula inteligente", "precio": 49.99, "valoracion": 4.2, "popularidad": 76, "categoria": "Hogar"},
	]
)

# Seleccionamos características numéricas para que el clasificador pueda compararlas.
feature_columns = ["precio", "valoracion", "popularidad"]
X = products[feature_columns]
y = products["categoria"]

# Separamos entrenamiento y prueba manteniendo la proporción de cada categoría.
X_train, X_test, y_train, y_test = train_test_split(
	X,
	y,
	test_size=0.25,
	random_state=42,
	stratify=y,
)

# El escalado evita que el precio, por su magnitud, domine las otras características.
# El Pipeline ajusta el escalador solo con los datos de entrenamiento y luego clasifica.
model = Pipeline(
	[
		("escalador", StandardScaler()),
		("clasificador", KNeighborsClassifier(n_neighbors=3)),
	]
)
model.fit(X_train, y_train)

# Generamos predicciones sobre productos reservados y mostramos una medida sencilla.
predictions = model.predict(X_test)
results = pd.DataFrame(
	{"categoria_real": y_test, "categoria_predicha": predictions},
	index=X_test.index,
)
print("Predicciones para los productos de prueba:")
print(results)
print(f"\nExactitud en prueba: {accuracy_score(y_test, predictions):.2f}")

# Guardamos los datos de entrenamiento en el mismo orden que usó el clasificador;
# sus posiciones permitirán asociar cada vecino cercano con el nombre del producto.
training_products = products.loc[X_train.index, ["producto", "categoria"]].reset_index(drop=True)


def recommend_products(product_name: str, number_of_recommendations: int = 3) -> list[str]:
	"""Recomienda productos de la categoría predicha más cercanos al producto dado."""
	# Buscamos el producto del catálogo y predecimos su categoría con sus características.
	product_row = products.loc[products["producto"] == product_name, feature_columns]
	if product_row.empty:
		raise ValueError(f"No se encontró el producto: {product_name}")

	predicted_category = model.predict(product_row)[0]

	# Obtenemos los vecinos por distancia dentro del conjunto de entrenamiento.
	scaler = model.named_steps["escalador"]
	classifier = model.named_steps["clasificador"]
	scaled_product = scaler.transform(product_row)
	neighbor_positions = classifier.kneighbors(
		scaled_product,
		n_neighbors=len(X_train),
		return_distance=False,
	)[0]

	# Conservamos vecinos de la categoría predicha y excluimos el producto consultado.
	recommendations = []
	for position in neighbor_positions:
		neighbor = training_products.iloc[position]
		if neighbor["categoria"] == predicted_category and neighbor["producto"] != product_name:
			recommendations.append(neighbor["producto"])
		if len(recommendations) == number_of_recommendations:
			break

	return recommendations


# Ejemplo de uso: se recomiendan productos similares al ratón inalámbrico.
example_product = "Ratón inalámbrico"
example_recommendations = recommend_products(example_product)
print(f"\nRecomendaciones para '{example_product}':")
for recommendation in example_recommendations:
	print(f"- {recommendation}")
