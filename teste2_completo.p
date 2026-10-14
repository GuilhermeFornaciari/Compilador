fn media(a:float,b:float)->float{
    return ( a + b ) / 2.5 ;
}

fn maior ( a : int , b : int ) -> int {
    if ( a >= b ) {
        return a ;
    } else {
        return b ;
    }
}

fn main ( ) {
    let letra : char = 'a' ;
    let sinal : char = '+' ;
    let traco : char = '_' ;
    let m : float = media ( 3.14 , 10.0 ) ;
    let n : int = maior ( 7 , 42 ) ;
    let r : int = 2 * 3 - 4 / 2 + 1 ;
    if ( n == 42 ) {
        println ( "n vale {} e m vale {}" , n , m ) ;
    }
    if ( n != 0 ) {
        println ( "letras: {} {} {}" , letra , sinal , traco ) ;
    }
    while ( r < 10 ) {
        r = r + 1 ;
    }
    if ( r <= 10 ) {
        println ( "fim" ) ;
    }
}
