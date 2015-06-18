#  Usage:
#   > options(width=150)
#   > source('visualizeData.R')

## 
## 
# lexical scope on color code and symbol code
# http://www.johndcook.com/R_language_for_programmers.html#scope
## put histograms on the diagonal
panel.summaryhist <- function(x, ...)
{
    usr <- par("usr"); on.exit(par(usr))
    par(usr = c(usr[1:2], 0, 2.5) )
    h <- hist(x, plot = FALSE)
    breaks <- h$breaks; nB <- length(breaks)
    y <- h$counts; y <- y/max(y)
    rect(breaks[-nB], 0, breaks[-1], y, col='cyan', ...)
    meanvalue <- mean(x)
    localdigits <- 4
    avgtxt <- paste("avg=", format( meanvalue , digits = localdigits ))
    stdtxt <- paste("std=", format( sd(x)     , digits = localdigits ))
    mintxt <- paste("min=", format( min(x)    , digits = localdigits ))
    maxtxt <- paste("max=", format( max(x)    , digits = localdigits ))
    #text(meanvalue , 1.2, mintxt )
    text(meanvalue , 1.2, avgtxt )
    text(meanvalue , 1.6, stdtxt )
    #text(meanvalue , 1.8, maxtxt )
    #if (do.legend) legend(43,2.5,c("GR","S2"), col = c(1,3), pch = c(1,3), bg="white")
    do.legend <<- FALSE
  
}
## put (absolute) correlations on the upper panels,
## with size proportional to the correlations.
panel.summarycor <- function(x, y, digits = 2, prefix = "", cex.cor, ...)
{
    usr <- par("usr"); on.exit(par(usr))
    par(usr = c(0, 1, 0, 1))
    r <- abs(cor(x, y))
    txt <- format(c(r, 0.123456789), digits = digits)[1]
    #if(cor(x, y) <  0.0) txt <- paste("cor=-", txt)
    #if(cor(x, y) >= 0.0) txt <- paste("cor=" , txt)
    if(missing(cex.cor)) cex.cor <- 0.8/strwidth(txt)
    #text(0.5, 0.5, txt, cex = cex.cor * r)
    text(0.5, 0.5, txt, cex = 1.)
}

# lexical scope on color code and symbol code
# http://www.johndcook.com/R_language_for_programmers.html#scope
panel.summarylinear <- function(x, y)
{
        points(x,y)
        #points(x,y,col=colcode,pch=symcode)
	abline(lm(y~x), col='red')
        #abline(h=CrossOver,v=CrossOver,col='blue',lty=2)
}

## load csv file
filename <- paste("datasummary", ".csv",sep="")
cat( filename , "\n" )
csvdata <- read.csv( filename ,header=TRUE , sep='\t',skip=0)
print(head(csvdata ,n=10))

## 
# plot cord summary
pdf("datasummarycord.pdf")
do.legend <- TRUE

pairs(~Voltage+NewEfieldAvgCord+AvgEfieldSpinalCord+DistanceProbeSpinalCord
        ,data=csvdata ,
        diag.panel  = panel.summaryhist, 
        lower.panel = panel.summarylinear,
        upper.panel = panel.summarycor,
       )
dev.off()

# plot root summary
pdf("datasummaryroot.pdf")
do.legend <- TRUE

pairs(~Voltage+NewEfieldAvgRoot+AvgEfieldNerveRoot+DistanceProbeNerveRoot
        ,data=csvdata ,
        diag.panel  = panel.summaryhist, 
        lower.panel = panel.summarylinear,
        upper.panel = panel.summarycor,
       )
dev.off()
