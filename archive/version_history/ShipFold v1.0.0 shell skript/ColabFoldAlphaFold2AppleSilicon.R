# ColabFold AlphaFold2 on Apple Silicon

# Difference in Runtime per Model ----
df_Intel_gfp_duration <- data.frame(run_one=c(896.3, 868.2, 803.8, 781.7, 793.5), run_two=c(945.9, 899.9, 825.3, 807.0, 812.0), run_three=c( 921.3, 893.5, 815.6, NA, NA)) # seconds
df_M1_gfp_duration <- data.frame(run_one=c(), run_two=c(), run_three=c()) # seconds
df_M3_gfp_duration <- data.frame(run_one=c(366.7, 373.6, 346.7, 347.4, 345.4), run_two=c(388.7, 405.2, 365.1, 358.5, 359.1), run_three=c(369.3, 391.5, 365.8, 360.0, 368.0)) # seconds

Intel_gfp_duration <- c(df_Intel_gfp_duration$run_one, df_Intel_gfp_duration$run_two, df_Intel_gfp_duration$run_three)
M1_gfp_duration <- c(df_M1_gfp_duration$run_one, df_M1_gfp_duration$run_two, df_M1_gfp_duration$run_three)
M3_gfp_duration <- c(df_M3_gfp_duration$run_one, df_M3_gfp_duration$run_two, df_M3_gfp_duration$run_three)
mean(M3_gfp_duration)

df_device_runtime <- data.frame(device = c (rep("Intel", length(Intel_gfp_duration)), 
                                            rep("M1", length(M1_gfp_duration)), 
                                            rep("M3", length(M3_gfp_duration))
                                            ), 
                                runtime=c(Intel_gfp_duration, M1_gfp_duration, M3_gfp_duration)
                                )
df_device_runtime

# ggplot2 boxplot
install.packages("ggplot2")
library(ggplot2)
ggplot(df_device_runtime, aes(device, runtime, fill = device)) + # fill = group
  geom_boxplot(color="black") +
  labs(x="Device", y="Runtime per Model [s]", title="Difference in Runtime per Model") + # adds lables
  scale_fill_manual(values = c("Intel"="grey", "M1"="skyblue", "M3"="navy")) + # adds colour fil by group
  theme(legend.position = "none") # position or remove legend
# Difference in CPU and RAM usage Protein Length and Device ----

df_CPU_RAM <- data.frame(device = c(rep("Intel", 2), rep("M1", 2), rep("M3", 2)), # rep amount of proteins used
                         protein_name = c(rep(c("GFP", "AKT"),3)),
                         protein_species = c(rep(c("AEQVI", "HUMAN"),3)),
                         protein_length = c(rep(c(238,480), 3)),
                         max_CPU_Intel_M1_M3 = c(61,NA,37,NA,NA,NA), # all Intel, then all M1, then all M3
                         max_RAM_Intel_M1_M3 = c(6.7,NA,6.6,NA,NA,NA)) # all Intel, then all M1, then all M3
df_CPU_RAM

# ggplot2 scatterplot CPU
ggplot(data=df_CPU_RAM, aes(protein_length, max_CPU_Intel_M1_M3, color=device)) + 
  geom_point() + # adds scatter
  geom_smooth(method="lm") + # adds linear regression line
  labs(x="Protein Length [aa]", y="Maximum CPU Usage [%]", title="CPU Usege Correlates to Protein Length") # adds lables

# ggplot2 scatterplot RAM
ggplot(data=df_CPU_RAM, aes(protein_length, max_RAM_Intel_M1_M3, color=device)) + 
  geom_point() + # adds scatter
  geom_smooth(method="lm") + # adds linear regression line
  labs(x="Protein Length [aa]", y="Maximum Memory Usage [GB]", title="Memory Usege Correlates to Protein Length") + # adds lables
  scale_y_continuous(labels = scales::number_format(accuracy = 0.1))
