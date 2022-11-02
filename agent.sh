#!/usr/bin/sh

echo 3b959fd8e286abdbc17bd2905a526ab5b7779e1500093afcaaace90d44bb9e45 > secret-file
curl -sO http://192.168.99.120:8080/jnlpJars/agent.jar
java -jar agent.jar -jnlpUrl http://192.168.99.120:8080/computer/svt/jenkins-agent.jnlp -secret @secret-file -workDir "/root" &
