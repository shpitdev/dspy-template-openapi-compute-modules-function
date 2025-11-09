export {};

const inputParam = encodeURIComponent(`I had severe nausea after taking Ozempic while on a roller coster at six flags.`);

const response = await fetch(`http://localhost:52910?input=${inputParam}`);
const data = await response.json();
console.log(JSON.stringify(data, null, 2));