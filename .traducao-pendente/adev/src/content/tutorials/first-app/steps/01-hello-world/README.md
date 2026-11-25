<!-- ia-translate: true -->

# Hello world

Esta primeira lição serve como ponto de partida a partir do qual cada lição neste tutorial adiciona novos recursos para construir uma aplicação Angular completa. Nesta lição, vamos atualizar a aplicação para exibir o famoso texto, "Hello World".

<docs-video src="https://www.youtube.com/embed/UnOwDuliqZA?si=uML-cDRbrxmYdD_9"/>

## O que você aprenderá {#what-youll-learn}

Se sua aplicação rodar com sucesso no navegador e exibir o conteúdo executado sem erros, isso confirma que seu ambiente de desenvolvimento e seu IDE estão configurados corretamente para começar a construir uma aplicação Angular.

NOTE: Se você estiver trabalhando com o editor incorporado, pule para o [passo quatro](#create-hello-world).
Ao trabalhar no playground do navegador, você não precisa executar `ng serve` para rodar a aplicação. Outros comandos como `ng generate` podem ser feitos na janela do console à sua direita.

<docs-workflow>

<docs-step title="Baixar a aplicação padrão {#download-the-default-app}">
Comece clicando no ícone "Download" no painel superior direito do editor de código. Isso fará o download de um arquivo `.zip` contendo o código-fonte para este tutorial. Abra isso em seu Terminal e IDE local e prossiga para testar a aplicação padrão.

Em qualquer etapa do tutorial, você pode clicar neste ícone para baixar o código-fonte da etapa e começar a partir daí.
</docs-step>

<docs-step title="Testar a aplicação padrão {#test-the-default-app}">
Neste passo, após baixar a aplicação inicial padrão, você constrói a aplicação Angular padrão.
Isso confirma que seu ambiente de desenvolvimento tem o que você precisa para continuar o tutorial.

No painel **Terminal** do seu IDE:

1. No diretório do seu projeto, navegue até o diretório `first-app`.
1. Execute este comando para instalar as dependências necessárias para rodar a aplicação.

   ```shell
   npm install
   ```

1. Execute este comando para construir e servir a aplicação padrão.

   ```shell
   ng serve
   ```

   A aplicação deve construir sem erros.

1. Em um navegador web no seu computador de desenvolvimento, abra `http://localhost:4200`.
1. Confirme que o site padrão aparece no navegador.
1. Você pode deixar o `ng serve` rodando enquanto completa os próximos passos.
   </docs-step>

<<<<<<< pt
<docs-step title="Revisar os arquivos do projeto {#review-the-files-in-the-project}">
Neste passo, você conhece os arquivos que compõem uma aplicação Angular padrão.

No painel **Explorer** do seu IDE:

1. No diretório do seu projeto, navegue até o diretório `first-app`.
1. Abra o diretório `src` para ver esses arquivos.
   1. No explorador de arquivos, encontre os arquivos da aplicação Angular (`/src`).
      1. `index.html` é o template HTML de nível superior da aplicação.
      1. `styles.css` é a folha de estilo de nível superior da aplicação.
      1. `main.ts` é onde a aplicação começa a rodar.
      1. `favicon.ico` é o ícone da aplicação, assim como você encontraria em qualquer site web.
   1. No explorador de arquivos, encontre os arquivos do component da aplicação Angular (`/app`).
      1. `app.ts` é o arquivo-fonte que descreve o component `app-root`.
         Este é o component Angular de nível superior na aplicação. Um component é o bloco de construção básico de uma aplicação Angular.
         A descrição do component inclui o código do component, template HTML e estilos, que podem ser descritos neste arquivo, ou em arquivos separados.

         Nesta aplicação, os estilos estão em um arquivo separado enquanto o código do component e o template HTML estão neste arquivo.

      1. `app.css` é a folha de estilo para este component.
      1. Novos components são adicionados a este diretório.

   1. No explorador de arquivos, encontre o diretório de imagens (`/public`) que contém imagens usadas pela aplicação.
   1. No explorador de arquivos, encontre os arquivos e diretórios que uma aplicação Angular precisa para construir e rodar, mas não são arquivos com os quais você normalmente interage.
      1. `.angular` tem arquivos necessários para construir a aplicação Angular.
      1. `.e2e` tem arquivos usados para testar a aplicação.
      1. `.node_modules` tem os pacotes node.js que a aplicação usa.
      1. `angular.json` descreve a aplicação Angular para as ferramentas de construção da aplicação.
      1. `package.json` é usado pelo `npm` (o gerenciador de pacotes node) para rodar a aplicação finalizada.
      1. `tsconfig.*` são os arquivos que descrevem a configuração da aplicação para o compilador TypeScript.

Depois de revisar os arquivos que compõem um projeto de aplicação Angular, continue para o próximo passo.
||||||| base_en
<docs-step title="Review the files in the project">
In this step, you get to know the files that make up a default Angular app.

In the **Explorer** pane of your IDE:

1. In your project directory, navigate to the `first-app` directory.
1. Open the `src` directory to see these files.
   1. In the file explorer, find the Angular app files (`/src`).
      1. `index.html` is the app's top level HTML template.
      1. `styles.css` is the app's top level style sheet.
      1. `main.ts` is where the app starts running.
      1. `favicon.ico` is the app's icon, just as you would find in any web site.
   1. In the file explorer, find the Angular app's component files (`/app`).
      1. `app.ts` is the source file that describes the `app-root` component.
         This is the top-level Angular component in the app. A component is the basic building block of an Angular application.
         The component description includes the component's code, HTML template, and styles, which can be described in this file, or in separate files.

         In this app, the styles are in a separate file while the component's code and HTML template are in this file.

      1. `app.css` is the style sheet for this component.
      1. New components are added to this directory.

   1. In the file explorer, find the image directory (`/public`) that contains images used by the app.
   1. In the file explorer, find the files and directories that an Angular app needs to build and run, but they are not files that you normally interact with.
      1. `.angular` has files required to build the Angular app.
      1. `.e2e` has files used to test the app.
      1. `.node_modules` has the node.js packages that the app uses.
      1. `angular.json` describes the Angular app to the app building tools.
      1. `package.json` is used by `npm` (the node package manager) to run the finished app.
      1. `tsconfig.*` are the files that describe the app's configuration to the TypeScript compiler.

After you have reviewed the files that make up an Angular app project, continue to the next step.
=======
<docs-step title="Review the files in the project">
In this step, you get to know the files that make up a default Angular app.

In the **Explorer** pane of your IDE:

1. In your project directory, navigate to the `first-app` directory.
1. Open the `src` directory to see these files.
   1. In the file explorer, find the Angular app files (`/src`).
      1. `index.html` is the app's top level HTML template.
      1. `styles.css` is the app's top level style sheet.
      1. `main.ts` is where the app starts running.
      1. `favicon.ico` is the app's icon, just as you would find in any web site.
   1. In the file explorer, find the Angular app's component files (`/app`).
      1. `app.ts` is the source file that describes the `app-root` component.
         This is the top-level Angular component in the app. A component is the basic building block of an Angular application.
         The component description includes the component's code, HTML template, and styles, which can be described in this file, or in separate files.

         In this app, the styles are in a separate file while the component's code and HTML template are in this file.

      1. `app.css` is the style sheet for this component.
      1. New components are added to this directory.

   1. In the file explorer, find the image directory (`/public`) that contains images used by the app.
   1. In the file explorer, find the files and directories that an Angular app needs to build and run. They are not files that you normally interact with.
      1. `.angular` has files required to build the Angular app.
      1. `.node_modules` has the node.js packages that the app uses.
      1. `angular.json` describes the Angular app to the app building tools.
      1. `package.json` is used by `npm` (the node package manager) to run the finished app.
      1. `tsconfig.*` are the files that describe the app's configuration to the TypeScript compiler.

After you have reviewed the files that make up an Angular app project, continue to the next step.
>>>>>>> new_en
</docs-step>

<docs-step title="Criar `Hello World` {#create-hello-world}">
Neste passo, você atualiza os arquivos do projeto Angular para mudar o conteúdo exibido.

No seu IDE:

1. Abra `first-app/src/index.html`.
   NOTE: Este passo e o próximo são apenas para seu ambiente local!

1. Em `index.html`, substitua o elemento `<title>` com este código para atualizar o título da aplicação.

   <docs-code header="Replace in src/index.html" path="adev/src/content/tutorials/first-app/steps/02-Home/src/index.html" visibleLines="[5]"/>

   Então, salve as alterações que você acabou de fazer em `index.html`.

1. Em seguida, abra `first-app/src/app/app.ts`.
1. Em `app.ts`, na definição do `@Component`, substitua a linha `template` com este código para alterar o texto no component da aplicação.

   <docs-code language="angular-ts" header="Replace in src/app/app.ts" path="adev/src/content/tutorials/first-app/steps/02-Home/src/app/app.ts" visibleLines="[6]"/>

1. Em `app.ts`, na definição da classe `App`, substitua a linha `title` com este código para alterar o título do component.

   <docs-code header="Replace in src/app/app.ts" path="adev/src/content/tutorials/first-app/steps/02-Home/src/app/app.ts" visibleLines="[10]"/>

   Então, salve as alterações que você fez em `app.ts`.

1. Se você parou o comando `ng serve` do passo 1, na janela **Terminal** do seu IDE, execute `ng serve` novamente.
1. Abra seu navegador e navegue para `localhost:4200` e confirme que a aplicação constrói sem erro e exibe _Homes_ no título e _Hello world_ no corpo da sua aplicação:
   <img alt="browser frame of page displaying the text 'Hello World'" src="assets/images/tutorials/first-app/homes-app-lesson-01-browser.png">
   </docs-step>

</docs-workflow>

SUMMARY: Nesta lição, você atualizou uma aplicação Angular padrão para exibir _Hello world_.
No processo, você aprendeu sobre o comando `ng serve` para servir sua aplicação localmente para testes.

Para mais informações sobre os tópicos cobertos nesta lição, visite:

<docs-pill-row>
  <docs-pill href="guide/components" title="Angular Components"/>
  <docs-pill href="tools/cli" title="Criando aplicações com o Angular CLI"/>
</docs-pill-row>
