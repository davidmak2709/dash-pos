#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    setuid( 0 );
    execvp( "/home/pi/dashvend/bin/show_image.sh", &argv[0] );
    return 0;
}
