// myscript.js
/**
* Devuelve una lista de los numeros primos menores que `max`.
*/
function getPrimes(max) {
    const isPrime = Array.from({ length: max }, () => true);
    isPrime[0] = isPrime[1] = false;
    isPrime[2] = true;
    for (let i = 2; i * i < max; i++) {
    if (isPrime[i]) {
    for (let j = i ** 2; j < max; j += i) {
    isPrime[j] = false;
    }
    }
    }
    return [...isPrime.entries()]
    .filter(([, isPrime]) => isPrime)
    .map(([number]) => number);
    }