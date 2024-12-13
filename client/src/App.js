import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  const [btn, setBtn] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:5000/')
      .then(response => response.json())
      .then(data => {
        setProducts(data.products);
        setBtn(data.btn);
      });
  }, []);

  return (
    <div>
      <Header btn={btn} />
      <Shop products={products} />
    </div>
  );
}

function Header({ btn }) {
  return (
    <div className="header">
      <a href={btn === 'LOGOUT' ? '/logout' : '/login'} className="home">
        {btn}
      </a>
      <h1 className="heading">Time After Time</h1>
      <a href="/cart" className="home">CART</a>
    </div>
  );
}

function Shop({ products }) {
  return (
    <>
      <h2 className="subheading">SHOP</h2>
      <Search />
      <div className="browse">
        <h2 className="box-head">Browse</h2>
        {products.map(product => (
          <a key={product.id} className="item" href={`/product/${product.id}`}>
            <img
              className="browse-picture"
              src={product.image}
              alt={`${product.name} Image`}
            />
            <div className="browse-title">{product.name}</div>
            <div className="price">₹{product.price}</div>
            <div className="description">{product.description}</div>
          </a>
        ))}
      </div>
    </>
  );
}

function Search() {
  return (
    <div className="search">
      <form action="/search_products" method="GET" className="search-container">
        <input
          type="text"
          className="search-bar"
          name="search_query"
          placeholder="Search for products..."
        />
      </form>
    </div>
  );
}

export default App;

