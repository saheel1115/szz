#based on unified file metric, this is code for file level bug prediction

library(faraway)
library(ROCR)
library(MASS)


source('~/bitbucket/err_corr/file_level_prediction/scripts/multiplot.R')



removeLeveragePoints<-function(bugData)
{ 
  
  ols <- lm(bug ~ log(commit_count+1) + log(own+1) + log(minor+1) 
               + log(sctr+1) + log(add+1) + log(del+1) + log(ddev+1) 
               + log(adev+1) + log(exp+1) + log(oexp+1) + log(nadd+1) 
               + log(ndel+1) + log(nsctr+1) + log(prev_bug+1),
            data = bugData)
  
  d1 <- cooks.distance(ols)
  r <- stdres(ols)
  a <- cbind(bugData, d1, r)
  ap = a[d1 <= 4/nrow(bugData), ]
  
  ap  
}



mylogit <- function(project_data) {
  
  
  m <- glm(bug > 0 ~ log(commit_count+1) + log(own+1) + log(minor+1) 
           + log(sctr+1) 
           + log(add+1) 
           + log(del+1)
           + log(ddev+1) 
           + log(adev+1) 
           + log(exp+1) 
           + log(oexp+1) 
           + log(nadd+1) 
           + log(ndel+1) 
           + log(nsctr+1) + log(prev_bug+1), 
           data = project_data,
           family = "binomial")
  
  return(m)
  
}




learnModel<-function(bugData, start_index) {
  bugData$snap_name = as.Date(bugData$snap_name)
  n <- length(unique(bugData$snap_name))
  snaps = sort(unique(bugData$snap_name))
  start_snap = sort(unique(bugData$snap_name))[start_index]
  
  models <- vector(mode="list", length=n)

  writeLines(paste("releaseNo = ", n))

  count = 0
  
  for(r in snaps) {
    count = count + 1

    learn_data = bugData[bugData$snap_name < r,]
    l = nrow(learn_data)
    if(l == 0) {
      writeLines(paste("skipping = ", count))
      next
    }
    m = mylogit(learn_data)
    
    
    release_data = bugData[bugData$snap_name == r,]
    models[[count]] = list(release=r, data=release_data, 
                       model=m)
    
   
  }
  
  return(models)
}



predictModel<-function(models,start_index) {
  
  
  releaseNo = length(models)
  
  
  for(r in start_index:releaseNo) {
    
    learn_model = models[[r]]$model
    models[[r]]$data$reg_predicted <- predict(learn_model, 
                                              newdata = models[[r]]$data, 
                                              type = "response")
   
  }
  
  return(models)
}







calROCR<-function(dataPoint, titleText="") {
  

  prob <- prediction(dataPoint$reg_predicted, dataPoint$isBug) 
                    
  tprfpr <- performance(prob, "tpr", "fpr")
  tpr <- unlist(slot(tprfpr, "y.values"))
  fpr <- unlist(slot(tprfpr, "x.values"))
  roc <- data.frame(tpr, fpr)
  auc <- performance(prob,"auc")
  auc <- unlist(slot(auc, "y.values"))
  auc <- round(auc, digits = 2)
  
  annText = sprintf('auc = %s', auc)
  
  p = ggplot(roc) + geom_line(aes(x = fpr, y = tpr)) + 
        geom_abline(intercept = 0, slope = 1, colour = "gray") + 
        ylab("Sensitivity") +
        xlab("1 - Specificity") +
        ggtitle(titleText)  +
        annotate("text", x = 0.7, y = 0.5, label = annText)
  
  return(p)
  
}



filePredict<-function(file_metric, project_name,isPlot=FALSE) {
  
  proj = file_metric[file_metric$proj_name==project_name,]
  #proj = removeLeveragePoints(proj) 
 
  projL = learnModel(proj, 2)
  projL = predictModel(projL, 2)
  
  if(isPlot == TRUE) {
    releases = order(unique(proj$snap_name))
  
    for(index in 2:length(releases)) {
      title_text = sprintf("%s-%s", project_name, index)
      print(title_text)
      projL[[index]]$plot = calROCR(projL[[index]]$data,title_text)
    }
  }
  
  proj_data = bind_data(projL,2)
  return(proj_data)

}

bind_data<-function(models,start_index) {
  
  releaseNo = length(models)
  df = data.frame()
  
  for(r in start_index:releaseNo) {
    
    df = rbind(df,models[[r]]$data)
  }
  df$isBug = ifelse(df$bug > 0, 1, 0)
  return(df)
}



main_all<-function() {
  
  fm = read.csv('data/final_file_metric.csv')
  
  atm = filePredict(fm, 'atmosphere',isPlot=FALSE)
  p_atm = calROCR(atm,'atmosphere')
  
  db  = filePredict(fm, 'derby',isPlot=FALSE)
  p_db = calROCR(db,'derby')
  
  el = filePredict(fm, 'elasticsearch',isPlot=FALSE)
  p_el = calROCR(el,'elasticsearch')
  
  fb = filePredict(fm, 'facebook-android-sdk',isPlot=FALSE)
  p_fb = calROCR(fb,'facebook')
  
  lu = filePredict(fm, 'lucene',isPlot=FALSE)
  p_lu = calROCR(lu,'lucene')
  
  nt = filePredict(fm, 'netty',isPlot=FALSE)
  p_nt = calROCR(nt,'netty')
  
  oj = filePredict(fm, 'openjpa',isPlot=FALSE)
  p_oj = calROCR(oj,'openjpa')
  
  pr = filePredict(fm, 'presto',isPlot=FALSE)
  p_pr = calROCR(pr,'presto')
  
  qp = filePredict(fm, 'qpid',isPlot=FALSE)
  p_qp = calROCR(fb,'qpid')
  
  wck = filePredict(fm, 'wicket',isPlot=FALSE)
  p_wck = calROCR(wck,'wicket')
    
  all=rbind(atm,db,fb,el,lu,nt,oj,pr,qp,wck)
  p_all = calROCR(all,'all')
  
  png("result/file_predict_roc_individual.png")
  multiplot(p_atm, p_db, p_el, p_fb, p_lu, 
            p_nt, p_oj, p_pr, p_qp, p_wck,
            cols=3)
  dev.off()
  
  png("result/file_predict_roc_all.png")
  p_all
  dev.off()
  
  write.csv(all,'data/file_predict.csv',row.names=FALSE)
  
}



