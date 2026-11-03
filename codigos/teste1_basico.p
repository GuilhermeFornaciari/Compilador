fn main ( ) {
    let x : int = 10 ;
    let soma : int = 0 ;
    while ( x > 0 ) {
        soma = soma + x ;
        x = x - 1 ;
    }
    println ( "soma = {}" , soma ) ;
}
